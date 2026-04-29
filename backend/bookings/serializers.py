from django.db import transaction
from rest_framework import serializers

from core.fields import hmac_value
from properties.models import Immoble
from .models import InquiliBasic, ReservaBasica, Hoste


class InquiliSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiliBasic
        fields = ['id', 'nom_complet', 'dni_passaport', 'email', 'dades_facturacio']
        read_only_fields = ['id']

    def validate_dni_passaport(self, value):
        h = hmac_value(value)
        qs = InquiliBasic.objects.filter(dni_passaport_hash=h)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ja existeix un inquilí amb aquest DNI/Passaport.")
        return value


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
            'codi_reserva', 'tipus_reserva', 'comentaris_interns', 'num_hostes',
            'hostes',
        ]
        read_only_fields = ['id', 'codi_reserva']

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

    @transaction.atomic
    def create(self, validated_data):
        hostes_data = validated_data.pop('hostes', [])
        reserva = ReservaBasica.objects.create(**validated_data)
        if hostes_data:
            self._replace_hostes(reserva, hostes_data)
            reserva.num_hostes = len(hostes_data)
            reserva.save(update_fields=['num_hostes'])
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
        return instance


class DashboardSerializer(serializers.Serializer):
    total_reserves = serializers.IntegerField()
    total_immobles = serializers.IntegerField()
    total_inquilins = serializers.IntegerField()
    immobles_actius = serializers.IntegerField()
    reserves_pagades = serializers.IntegerField()
