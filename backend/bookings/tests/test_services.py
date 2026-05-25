# backend/bookings/tests/test_services.py
from datetime import date
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from bookings.services import calcular_preview_reserva
from properties.models import Immoble, Temporada


def _data(immoble_pk, **kwargs):
    base = {
        "immoble": immoble_pk,
        "data_entrada": "2025-07-01",
        "data_sortida": "2025-07-05",  # 4 nits
        "num_hostes": 2,
        "descompte_immoble_aplicat": False,
        "descompte_immoble_percentatge": 0,
        "descompte_individual_aplicat": False,
        "descompte_individual_percentatge": 0,
    }
    base.update(kwargs)
    return base


class MinNitsValidacioTest(TestCase):
    def setUp(self):
        self.immoble = Immoble.objects.create(
            nom_comercial="Pis Test",
            adreca="Carrer Test 1",
            preu_base_nit=50,
        )

    def test_min_nits_complert_no_llanca_error(self):
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Estiu",
            data_inici=date(2000, 6, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=100,
            min_nits=3,
        )
        result = calcular_preview_reserva(_data(self.immoble.pk))
        self.assertEqual(result["nits"], 4)

    def test_min_nits_no_complert_llanca_error(self):
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Estiu",
            data_inici=date(2000, 6, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=100,
            min_nits=7,
        )
        with self.assertRaises(ValidationError) as ctx:
            calcular_preview_reserva(_data(self.immoble.pk))
        detail = str(ctx.exception.detail)
        self.assertIn("7", detail)
        self.assertIn("Estiu", detail)
        self.assertIn("4", detail)

    def test_min_nits_mes_restrictiu_bloca_reserva(self):
        # Booking spanning 2 temporades: 2025-07-30 a 2025-08-03 = 4 nits
        # T1 (juliol): min_nits=2 — OK
        # T2 (agost): min_nits=7 — KO
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Juliol",
            data_inici=date(2000, 7, 1),
            data_fi=date(2000, 7, 31),
            preu_nit=90,
            min_nits=2,
        )
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Agost",
            data_inici=date(2000, 8, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=120,
            min_nits=7,
        )
        with self.assertRaises(ValidationError):
            calcular_preview_reserva(_data(
                self.immoble.pk,
                data_entrada="2025-07-30",
                data_sortida="2025-08-03",  # 4 nits, Agost requereix 7
            ))


class AvisSenseTemporadaTest(TestCase):
    def setUp(self):
        self.immoble = Immoble.objects.create(
            nom_comercial="Pis Sense Temporada",
            adreca="Carrer Test 2",
            preu_base_nit=60,
        )

    def test_sense_temporada_retorna_llista_dates(self):
        result = calcular_preview_reserva(_data(self.immoble.pk))
        self.assertIn("avis_sense_temporada", result)
        self.assertEqual(len(result["avis_sense_temporada"]), 4)
        self.assertIn("2025-07-01", result["avis_sense_temporada"])
        self.assertIn("2025-07-04", result["avis_sense_temporada"])

    def test_amb_temporada_completa_llista_buida(self):
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Estiu",
            data_inici=date(2000, 6, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=80,
            min_nits=1,
        )
        result = calcular_preview_reserva(_data(self.immoble.pk))
        self.assertEqual(result["avis_sense_temporada"], [])

    def test_temporada_parcial_retorna_dates_sense_cobrir(self):
        # Temporada cobreix juliol però no agost
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Juliol",
            data_inici=date(2000, 7, 1),
            data_fi=date(2000, 7, 31),
            preu_nit=80,
            min_nits=1,
        )
        # Booking: 30 juliol - 3 agost (4 nits: 30 jul, 31 jul, 1 ago, 2 ago)
        # 30-31 jul cobertes, 1-2 ago no cobertes
        result = calcular_preview_reserva(_data(
            self.immoble.pk,
            data_entrada="2025-07-30",
            data_sortida="2025-08-03",
        ))
        self.assertIn("2025-08-01", result["avis_sense_temporada"])
        self.assertIn("2025-08-02", result["avis_sense_temporada"])
        self.assertNotIn("2025-07-30", result["avis_sense_temporada"])
        self.assertNotIn("2025-07-31", result["avis_sense_temporada"])
