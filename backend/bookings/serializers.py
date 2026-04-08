from rest_framework import serializers
from .models import Inquili, Reserva, ReservaHostes


class InquiliSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquili
        fields = '__all__'


class ReservaHostesSerializer(serializers.ModelSerializer):
    hoste_nom = serializers.CharField(source='hoste.nom', read_only=True)

    class Meta:
        model = ReservaHostes
        fields = ['id', 'hoste', 'hoste_nom', 'es_principal']


class ReservaSerializer(serializers.ModelSerializer):
    hostes = ReservaHostesSerializer(many=True, read_only=True)
    immoble_nom = serializers.CharField(source='immoble.nom_comercial', read_only=True)
    inquili_nom = serializers.CharField(source='inquili_principal.nom', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'immoble', 'immoble_nom', 'inquili_principal', 'inquili_nom',
            'data_entrada', 'data_sortida', 'preu_total', 'taxa_turistica',
            'estat', 'hostes',
        ]
        read_only_fields = ['id']


class DashboardSerializer(serializers.Serializer):
    total_reserves = serializers.IntegerField()
    total_immobles = serializers.IntegerField()
    total_inquilins = serializers.IntegerField()
    immobles_actius = serializers.IntegerField()
    reserves_confirmades = serializers.IntegerField()
