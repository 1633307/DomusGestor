from django.db import transaction
from rest_framework import serializers

from core.fields import hmac_value
from properties.models import Immoble

from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste, Comunicacio, PagamentReserva, ComunicacioEmail


def _has_value(value):
    return value is not None and value != ''


def _can_use_document_for_persona(persona, document):
    if not document:
        return False
    document_hash = hmac_value(document)
    return not (
        Persona.objects
        .filter(dni_passaport_hash=document_hash)
        .exclude(pk=persona.pk)
        .exists()
    )


def sync_persona_from_hoste(persona, hoste, overwrite=False):
    if persona is None or hoste is None:
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

    for hoste_field, persona_field in field_map:
        source_value = getattr(hoste, hoste_field, None)
        current_value = getattr(persona, persona_field, None)
        if _has_value(source_value) and (overwrite or not _has_value(current_value)):
            setattr(persona, persona_field, source_value)
            changed_fields.append(persona_field)

    if _has_value(getattr(hoste, 'numero_document', None)):
        current_document = getattr(persona, 'dni_passaport', None)
        if (overwrite or not _has_value(current_document)) and _can_use_document_for_persona(
            persona, hoste.numero_document,
        ):
            persona.dni_passaport = hoste.numero_document
            changed_fields.append('dni_passaport')

    if changed_fields:
        update_fields = sorted(set(changed_fields + ['dni_passaport_hash']))
        persona.save(update_fields=update_fields)

    return changed_fields


class PerfilInquiliSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilInquili
        fields = ['id']


class PerfilPropietariSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilPropietari
        fields = [
            'id', 'persona', 'nom_fiscal', 'nif_cif', 'adreca_facturacio',
            'codi_postal_facturacio', 'ciutat_facturacio', 'provincia_facturacio',
            'pais_facturacio', 'email_facturacio', 'telefon_facturacio',
            'iban', 'observacions_facturacio',
        ]
        extra_kwargs = {'persona': {'required': True}}


class PersonaSerializer(serializers.ModelSerializer):
    perfil_inquili = PerfilInquiliSerializer(read_only=True)
    perfil_propietari = PerfilPropietariSerializer(read_only=True)
    reserves = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = [
            'id', 'nom_complet', 'genere', 'tipus_document', 'dni_passaport',
            'nacionalitat', 'data_naixement', 'residencia', 'email', 'telefon',
            'perfil_inquili', 'perfil_propietari', 'reserves',
        ]
        read_only_fields = ['id']

    def validate_dni_passaport(self, value):
        if not value:
            return value
        h = hmac_value(value)
        qs = Persona.objects.filter(dni_passaport_hash=h)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ja existeix una persona amb aquest DNI/Passaport.")
        return value

    def to_internal_value(self, data):
        cleaned = dict(data)
        if cleaned.get('data_naixement') in ('', None):
            cleaned['data_naixement'] = None
        return super().to_internal_value(cleaned)

    def get_reserves(self, obj):
        return [
            {
                'id': r.id,
                'codi_reserva': r.codi_reserva,
                'immoble_nom': r.immoble.nom_comercial,
                'data_entrada': str(r.data_entrada),
                'data_sortida': str(r.data_sortida),
                'estat_reserva': r.estat_reserva,
            }
            for r in obj.reserves.select_related('immoble').all()
        ]


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
            raise serializers.ValidationError("El descompte individual ha d'estat entre 0 i 100.")
        return value

    def _replace_hostes(self, reserva, hostes_data):
        reserva.hostes.all().delete()
        principal_assigned = False
        new_hostes = []
        for h_data in hostes_data:
            es_principal = bool(h_data.get('es_principal'))
            if es_principal and principal_assigned:
                es_principal = False
            if es_principal:
                principal_assigned = True
            payload = {**h_data, 'es_principal': es_principal, 'reserva': reserva}
            new_hostes.append(Hoste(**payload))
        if new_hostes and not principal_assigned:
            new_hostes[0].es_principal = True
        for h in new_hostes:
            h.save()

    def _sync_persona_from_principal_hoste(self, reserva):
        hoste_principal = reserva.hostes.filter(es_principal=True).first()
        sync_persona_from_hoste(reserva.inquili, hoste_principal, overwrite=False)

    @transaction.atomic
    def create(self, validated_data):
        hostes_data = validated_data.pop('hostes', [])
        reserva = ReservaBasica.objects.create(**validated_data)
        if hostes_data:
            self._replace_hostes(reserva, hostes_data)
            reserva.num_hostes = len(hostes_data)
            reserva.save(update_fields=['num_hostes'])
        self._sync_persona_from_principal_hoste(reserva)
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
        self._sync_persona_from_principal_hoste(instance)
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
    inquili_nom = serializers.CharField(source='reserva.inquili.nom_complet', read_only=True)

    class Meta:
        model = PagamentReserva
        fields = [
            'id', 'reserva', 'codi_reserva', 'inquili_nom',
            'data_pagament', 'import_pagament', 'metode_pagament', 'estat',
        ]
        read_only_fields = ['id']


class ComunicacioEmailSerializer(serializers.ModelSerializer):
    enviat_per_nom = serializers.CharField(source='enviat_per.username', read_only=True, default=None)

    class Meta:
        model = ComunicacioEmail
        fields = ['id', 'tipus', 'destinatari', 'assumpte', 'enviat_a', 'enviat_per', 'enviat_per_nom', 'exit', 'error_msg']
        read_only_fields = fields


class DashboardSerializer(serializers.Serializer):
    total_reserves = serializers.IntegerField()
    total_immobles = serializers.IntegerField()
    total_inquilins = serializers.IntegerField()
    immobles_actius = serializers.IntegerField()
    reserves_pagades = serializers.IntegerField()
