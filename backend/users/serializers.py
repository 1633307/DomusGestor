from rest_framework import serializers

from .models import Usuari, InfoImmobiliaria


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
            raise serializers.ValidationError('Compte desactivat.')

        data['user'] = user
        return data


class UsuariSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuari
        fields = ['id', 'username', 'email', 'nip']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuari
        fields = ['username', 'email', 'nip', 'password']

    def validate_nip(self, value):
        if Usuari.objects.filter(nip_hash=hmac_value(value)).exists():
            raise serializers.ValidationError("Ja existeix un usuari amb aquest NIP.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuari(**validated_data)
        user.set_password(password)
        user.save()
        return user


class InfoImmobiliariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoImmobiliaria
        fields = '__all__'
