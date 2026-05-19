from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError

from properties.models import Immoble


DEFAULT_COMISSIO_PERCENT = Decimal("15.00")
# TODO: Ajustar aquest import segons normativa vigent i criteri del client.
TAXA_TURISTICA_PER_HOSTE_NIT = Decimal("1.00")
TWOPLACES = Decimal("0.01")


def _money(value):
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _percent(value):
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _to_decimal(value, field_name):
    try:
        return Decimal(str(value or "0"))
    except Exception as exc:
        raise ValidationError({field_name: "Valor numeric invalid."}) from exc


def _to_bool(value):
    return value is True or value in ("true", "True", "Si", "Sí", "si", "sí", "1", 1)


def _validate_percent(value, field_name):
    decimal_value = _to_decimal(value, field_name)
    if decimal_value < 0 or decimal_value > 100:
        raise ValidationError({field_name: "El percentatge ha d'estar entre 0 i 100."})
    return decimal_value


def _season_date(day):
    return day.replace(year=2000)


def _temporada_for_day(temporades, day):
    season_day = _season_date(day)
    for temporada in temporades:
        start = temporada.data_inici
        end = temporada.data_fi
        if start <= end:
            if start <= season_day <= end:
                return temporada
        elif season_day >= start or season_day <= end:
            return temporada
    return None


def calcular_preview_reserva(data):
    try:
        immoble_id = int(data.get("immoble"))
    except (TypeError, ValueError) as exc:
        raise ValidationError({"immoble": "Immoble invalid."}) from exc

    try:
        immoble = Immoble.objects.prefetch_related("temporades").get(pk=immoble_id)
    except Immoble.DoesNotExist as exc:
        raise ValidationError({"immoble": "No s'ha trobat l'immoble."}) from exc

    data_entrada = parse_date(str(data.get("data_entrada") or ""))
    data_sortida = parse_date(str(data.get("data_sortida") or ""))
    if not data_entrada:
        raise ValidationError({"data_entrada": "La data d'entrada es obligatoria."})
    if not data_sortida:
        raise ValidationError({"data_sortida": "La data de sortida es obligatoria."})

    nits = (data_sortida - data_entrada).days
    if nits <= 0:
        raise ValidationError({"data_sortida": "La data de sortida ha de ser posterior a la data d'entrada."})

    try:
        num_hostes = int(data.get("num_hostes") or 0)
    except (TypeError, ValueError) as exc:
        raise ValidationError({"num_hostes": "El nombre d'hostes es invalid."}) from exc
    if num_hostes < 1:
        raise ValidationError({"num_hostes": "El nombre d'hostes ha de ser com a minim 1."})

    descompte_immoble_actiu = _to_bool(data.get("descompte_immoble_aplicat"))
    descompte_individual_actiu = _to_bool(data.get("descompte_individual_aplicat"))
    descompte_immoble_percent = (
        _validate_percent(data.get("descompte_immoble_percentatge"), "descompte_immoble_percentatge")
        if descompte_immoble_actiu
        else Decimal("0")
    )
    descompte_individual_percent = (
        _validate_percent(data.get("descompte_individual_percentatge"), "descompte_individual_percentatge")
        if descompte_individual_actiu
        else Decimal("0")
    )

    temporades = list(immoble.temporades.all())
    linies_nits = []
    subtotal = Decimal("0")
    current_day = data_entrada

    while current_day < data_sortida:
        temporada = _temporada_for_day(temporades, current_day)
        preu_nit = Decimal(temporada.preu_nit if temporada else immoble.preu_base_nit)
        comissio_percent = Decimal(temporada.comissio if temporada else DEFAULT_COMISSIO_PERCENT)
        subtotal += preu_nit
        linies_nits.append(
            {
                "data": current_day.isoformat(),
                "preu_nit": str(_money(preu_nit)),
                "temporada": temporada.nom if temporada else None,
                "comissio_percentatge": str(_percent(comissio_percent)),
                "_preu_nit": preu_nit,
                "_comissio_percentatge": comissio_percent,
            }
        )
        current_day += timedelta(days=1)

    descompte_immoble_import = subtotal * descompte_immoble_percent / Decimal("100")
    base_despres_immoble = subtotal - descompte_immoble_import
    descompte_individual_import = base_despres_immoble * descompte_individual_percent / Decimal("100")
    total_allotjament = base_despres_immoble - descompte_individual_import

    factor_descompte = Decimal("1")
    if descompte_immoble_actiu:
        factor_descompte *= Decimal("1") - (descompte_immoble_percent / Decimal("100"))
    if descompte_individual_actiu:
        factor_descompte *= Decimal("1") - (descompte_individual_percent / Decimal("100"))

    comissio_import = sum(
        linia["_preu_nit"] * factor_descompte * linia["_comissio_percentatge"] / Decimal("100")
        for linia in linies_nits
    )
    # La comissio es informativa per a la immobiliaria; no s'afegeix al total del turista.
    comissio_percentatge_mitjana = (
        (comissio_import / total_allotjament * Decimal("100"))
        if total_allotjament > 0
        else Decimal("0")
    )

    taxa_turistica_import = Decimal(num_hostes) * Decimal(nits) * TAXA_TURISTICA_PER_HOSTE_NIT
    total_a_abonar_turista = total_allotjament + taxa_turistica_import

    for linia in linies_nits:
        linia.pop("_preu_nit", None)
        linia.pop("_comissio_percentatge", None)

    return {
        "nits": nits,
        "num_hostes": num_hostes,
        "subtotal_allotjament": str(_money(subtotal)),
        "descompte_immoble_percentatge": str(_percent(descompte_immoble_percent)),
        "descompte_immoble_import": str(_money(descompte_immoble_import)),
        "descompte_individual_percentatge": str(_percent(descompte_individual_percent)),
        "descompte_individual_import": str(_money(descompte_individual_import)),
        "total_allotjament": str(_money(total_allotjament)),
        "comissio_percentatge_mitjana": str(_percent(comissio_percentatge_mitjana)),
        "comissio_import": str(_money(comissio_import)),
        "taxa_turistica_per_hoste_nit": str(_money(TAXA_TURISTICA_PER_HOSTE_NIT)),
        "taxa_turistica_import": str(_money(taxa_turistica_import)),
        "total_a_abonar_turista": str(_money(total_a_abonar_turista)),
        "linies_nits": linies_nits,
    }
