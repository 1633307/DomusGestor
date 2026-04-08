from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Usuari, Propietari


class LoginSerializer(serializers.Serializer):
    nip = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        nip = data.get('nip')
        password = data.get('password')

        try:
            user = Usuari.objects.get(nip=nip)
        except Usuari.DoesNotExist:
            raise serializers.ValidationError('Credencials incorrectes.')

        if not user.check_password(password):
            raise serializers.ValidationError('Credencials incorrectes.')

        if not user.is_active:
            raise serializers.ValidationError("Compte desactivat.")

        data['user'] = user
        return data


class UsuariSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuari
        fields = ['id', 'username', 'email', 'nip', 'rol', 'first_name', 'last_name']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuari
        fields = ['username', 'email', 'nip', 'rol', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuari(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PropietariSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietari
        fields = '__all__'
