from rest_framework import serializers

from core.fields import hmac_value
from properties.models import Immoble
from .models import InquiliBasic, ReservaBasica


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


class ReservaSerializer(serializers.ModelSerializer):
    immoble_nom = serializers.CharField(source='immoble.nom_comercial', read_only=True)
    inquili_nom = serializers.CharField(source='inquili.nom_complet', read_only=True)

    class Meta:
        model = ReservaBasica
        fields = [
            'id', 'immoble', 'immoble_nom', 'inquili', 'inquili_nom',
            'data_entrada', 'data_sortida', 'pagat',
        ]
        read_only_fields = ['id']


class DashboardSerializer(serializers.Serializer):
    total_reserves = serializers.IntegerField()
    total_immobles = serializers.IntegerField()
    total_inquilins = serializers.IntegerField()
    immobles_actius = serializers.IntegerField()
    reserves_pagades = serializers.IntegerField()
