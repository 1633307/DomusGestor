from rest_framework import serializers
from .models import Immoble, Temporada


class TemporadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporada
        fields = '__all__'


class ImmobleSerializer(serializers.ModelSerializer):
    temporades = TemporadaSerializer(many=True, read_only=True)
    propietari_nom = serializers.CharField(source='propietari.nom', read_only=True, default=None)

    class Meta:
        model = Immoble
        fields = [
            'id', 'propietari', 'propietari_nom', 'nom_comercial', 'adreca',
            'preu_base', 'estat_neteja', 'info_tecnica',
            'metres_quadrats', 'num_habitacions', 'num_banys',
            'capacitat_maxima', 'descripcio', 'actiu', 'data_registre',
            'temporades',
        ]
        read_only_fields = ['id', 'data_registre']


class ImmobleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Immoble
        fields = [
            'propietari', 'nom_comercial', 'adreca', 'preu_base',
            'estat_neteja', 'info_tecnica',
            'metres_quadrats', 'num_habitacions', 'num_banys',
            'capacitat_maxima', 'descripcio', 'actiu',
        ]
