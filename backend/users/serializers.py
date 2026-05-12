from rest_framework import serializers
from .models import Usuari, InfoImmobiliaria


class LoginSerializer(serializers.Serializer):
    nip      = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = Usuari.objects.get(nip=data['nip'])
        except Usuari.DoesNotExist:
            raise serializers.ValidationError('Credencials incorrectes.')

        if not user.check_password(data['password']):
            raise serializers.ValidationError('Credencials incorrectes.')

        if not user.is_active:
            raise serializers.ValidationError('Compte desactivat.')

        data['user'] = user
        return data


class UsuariSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Usuari
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'nip', 'is_admin', 'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined', 'is_admin']


class CreateUsuariSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = Usuari
        fields = ['username', 'first_name', 'last_name', 'email', 'nip', 'password', 'is_admin']

    def validate_nip(self, value):
        if Usuari.objects.filter(nip=value).exists():
            raise serializers.ValidationError("Ja existeix un usuari amb aquest NIP.")
        return value

    def validate_email(self, value):
        if Usuari.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ja existeix un usuari amb aquest email.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuari(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateUsuariSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Usuari
        fields = ['username', 'first_name', 'last_name', 'email', 'nip', 'is_admin']

    def validate_nip(self, value):
        qs = Usuari.objects.filter(nip=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ja existeix un usuari amb aquest NIP.")
        return value

    def validate_email(self, value):
        qs = Usuari.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ja existeix un usuari amb aquest email.")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = Usuari
        fields = ['username', 'email', 'nip', 'password']

    def validate_nip(self, value):
        if Usuari.objects.filter(nip=value).exists():
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
        model  = InfoImmobiliaria
        fields = '__all__'
