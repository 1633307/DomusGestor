from rest_framework import serializers

from .models import Immoble


class ImmobleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Immoble
        fields = '__all__'
        read_only_fields = ['id', 'data_registre']

    def validate_descompte_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descompte ha d'estar entre 0 i 100.")
        return value
