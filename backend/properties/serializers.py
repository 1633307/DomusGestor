from rest_framework import serializers

from .models import Immoble


class ImmobleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Immoble
        fields = '__all__'
        read_only_fields = ['id', 'data_registre']
