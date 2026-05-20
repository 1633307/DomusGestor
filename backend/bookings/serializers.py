from django.db import transaction
from rest_framework import serializers

from core.fields import hmac_value
from properties.models import Immoble

from .models import InquiliBasic, ReservaBasica, Hoste, Comunicacio, PagamentReserva


def _has_value(value):
    return value is not None and value != ''


def _can_use_document_for_inquili(inquili, document):
    if not document:
        return False

    document_hash = hmac_value(document)
    return not (
        InquiliBasic.objects
        .filter(dni_passaport_hash=document_hash)
        .exclude(pk=inquili.pk)
        .exists()
    )


def sync_inquili_from_hoste(inquili, hoste, overwrite=False):
    if inquili is None or hoste is None:
        return []

    changed_fields = []
    field_map = [
        ('nom_complet', 'nom_complet'),
        ('genere', 'genere'),
        ('tipus_document', 'tipus_document'),
        ('nacionalitat', 'nacionalitat'),
        ('data_naixement', 'data_naixement'),
        ('residencia', 'residencia'),
        ('email', 'email'),
        ('telefon', 'telefon'),
    ]

    for hoste_field, inquili_field in field_map:
        source_value = getattr(hoste, hoste_field, None)
        current_value = getattr(inquili, inquili_field, None)
        if _has_value(source_value) and (overwrite or not _has_value(current_value)):
            setattr(inquili, inquili_field, source_value)
            changed_fields.append(inquili_field)

    if _has_value(getattr(hoste, 'numero_document', None)):
        current_document = getattr(inquili, 'dni_passaport', None)
        if (overwrite or not _has_value(current_document)) and _can_use_document_for_inquili(
            inquili,
            hoste.numero_document,
        ):
            inquili.dni_passaport = hoste.numero_document
            changed_fields.append('dni_passaport')

    if changed_fields:
        update_fields = sorted(set(changed_fields + ['dni_passaport_hash']))
        inquili.save(update_fields=update_fields)

    return changed_fields


class InquiliSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiliBasic
        fields = [
            'id', 'nom_complet', 'dni_passaport', 'email', 'dades_facturacio',
            'genere', 'tipus_document', 'nacionalitat', 'data_naixement',
            'residencia', 'telefon', 'nom_fiscal', 'nif_cif',
            'adreca_facturacio', 'codi_postal_facturacio', 'ciutat_facturacio',
            'provincia_facturacio', 'pais_facturacio', 'email_facturacio',
            'telefon_facturacio', 'observacions_facturacio',
        ]
        read_only_fields = ['id']

    def validate_dni_passaport(self, value):
        if not value:
            return value
        h = hmac_value(value)
        qs = InquiliBasic.objects.filter(dni_passaport_hash=h)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ja existeix un inquilí amb aquest DNI/Passaport.")
        return value

    def to_internal_value(self, data):
        cleaned = dict(data)
        if cleaned.get('data_naixement') in ('', None):
            cleaned['data_naixement'] = None
        return super().to_internal_value(cleaned)


class HosteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hoste
        fields = [
            'id', 'es_principal', 'nom_complet', 'genere', 'relacio_parental',
            'tipus_document', 'numero_document', 'nacionalitat',
            'data_naixement', 'residencia', 'email', 'telefon',
        ]
        read_only_fields = ['id']

    def to_internal_value(self, data):
        # Permet que data_naixement sigui '' (la frontend pot enviar string buit)
        cleaned = dict(data)
        if cleaned.get('data_naixement') in ('', None):
            cleaned['data_naixement'] = None
        return super().to_internal_value(cleaned)


class ReservaSerializer(serializers.ModelSerializer):
    immoble_nom = serializers.CharField(source='immoble.nom_comercial', read_only=True)
    inquili_nom = serializers.CharField(source='inquili.nom_complet', read_only=True)
    hostes = HosteSerializer(many=True, required=False)

    class Meta:
        model = ReservaBasica
        fields = [
            'id', 'immoble', 'immoble_nom', 'inquili', 'inquili_nom',
            'data_entrada', 'data_sortida', 'pagat',
            'codi_reserva', 'tipus_reserva', 'estat_reserva', 'net',
            'comentaris_interns', 'num_hostes',
            'descompte_immoble_aplicat', 'descompte_immoble_percentatge',
            'descompte_individual_aplicat', 'descompte_individual_percentatge',
            'descompte_individual_motiu',
            'estat_pagament', 'import_total', 'import_pagat', 'import_pendent',
            'fianca', 'metode_pagament', 'data_ultim_pagament',
            'observacions_pagament',
            'hostes',
        ]
        read_only_fields = ['id', 'codi_reserva']

    def validate_descompte_immoble_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descompte de l'immoble ha d'estar entre 0 i 100.")
        return value

    def validate_descompte_individual_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descompte individual ha d'estar entre 0 i 100.")
        return value

    def _replace_hostes(self, reserva, hostes_data):
        """Esborra els hostes existents i en crea de nous a partir de la llista."""
        reserva.hostes.all().delete()
        principal_assigned = False
        new_hostes = []
        for idx, h_data in enumerate(hostes_data):
            # Garantim que només hi hagi un hoste principal
            es_principal = bool(h_data.get('es_principal'))
            if es_principal and principal_assigned:
                es_principal = False
            if es_principal:
                principal_assigned = True
            payload = {**h_data, 'es_principal': es_principal, 'reserva': reserva}
            new_hostes.append(Hoste(**payload))
        # Si no n'hi ha cap de marcat, fem el primer com a principal
        if new_hostes and not principal_assigned:
            new_hostes[0].es_principal = True
        # Crear-los individualment perquè el save() generi el hash del document
        for h in new_hostes:
            h.save()

    def _sync_inquili_from_principal_hoste(self, reserva):
        hoste_principal = reserva.hostes.filter(es_principal=True).first()
        sync_inquili_from_hoste(reserva.inquili, hoste_principal, overwrite=False)

    @transaction.atomic
    def create(self, validated_data):
        hostes_data = validated_data.pop('hostes', [])
        reserva = ReservaBasica.objects.create(**validated_data)
        if hostes_data:
            self._replace_hostes(reserva, hostes_data)
            reserva.num_hostes = len(hostes_data)
            reserva.save(update_fields=['num_hostes'])
        self._sync_inquili_from_principal_hoste(reserva)
        return reserva

    @transaction.atomic
    def update(self, instance, validated_data):
        hostes_data = validated_data.pop('hostes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if hostes_data is not None:
            self._replace_hostes(instance, hostes_data)
            instance.num_hostes = len(hostes_data)
            instance.save(update_fields=['num_hostes'])
        self._sync_inquili_from_principal_hoste(instance)
        return instance


class ComunicacioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunicacio
        fields = [
            'id', 'reserva', 'canal', 'titol', 'destinatari',
            'data', 'estat', 'resum', 'creat_el',
        ]
        read_only_fields = ['id', 'creat_el', 'reserva']

    def to_internal_value(self, data):
        cleaned = dict(data)
        if cleaned.get('data') in ('', None):
            cleaned['data'] = None
        return super().to_internal_value(cleaned)
class PagamentReservaSerializer(serializers.ModelSerializer):
    codi_reserva = serializers.CharField(source='reserva.codi_reserva', read_only=True)
    inquili_nom  = serializers.CharField(source='reserva.inquili.nom_complet', read_only=True)

    class Meta:
        model = PagamentReserva
        fields = [
            'id', 'reserva', 'codi_reserva', 'inquili_nom',
            'data_pagament', 'import_pagament', 'metode_pagament', 'estat',
        ]
        read_only_fields = ['id']


class DashboardSerializer(serializers.Serializer):
    total_reserves = serializers.IntegerField()
    total_immobles = serializers.IntegerField()
    total_inquilins = serializers.IntegerField()
    immobles_actius = serializers.IntegerField()
    reserves_pagades = serializers.IntegerField()
