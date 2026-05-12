from rest_framework import serializers

from .models import Immoble, Servei, Temporada


class ServeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servei
        fields = '__all__'


class TemporadaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Temporada
        fields = '__all__'
        extra_kwargs = {
            "immoble": {"required": False}
        }

    def validate_data_inici(self, value):
        return value.replace(year=2000)

    def validate_data_fi(self, value):
        return value.replace(year=2000)


class ImmobleSerializer(serializers.ModelSerializer):
    temporades = TemporadaSerializer(many=True, required=False)

    class Meta:
        model = Immoble
        fields = '__all__'
        read_only_fields = ['id', 'data_registre']

    def validate_descompte_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "El descompte ha d'estar entre 0 i 100.")
        return value

    def update(self, instance, validated_data):
        temporades_data = validated_data.pop('temporades', [])

        # 1. editar l'immoble
        instance = super().update(instance, validated_data)

        # 2. editar les temporades

        # 2.1. agafem les ids de les temporades que ens han arribat
        incoming_ids = [t.get('id') for t in temporades_data if t.get('id')]

        # 2.2. eliminem les temporades d'aquest immoble que no ens han enviades
        Temporada.objects.filter(
            immoble=instance
        ).exclude(id__in=incoming_ids).delete()

        # 2.3. creem o editem cada temporada rebuda
        for t_data in temporades_data:
            t_id = t_data.get('id')

            if t_id:
                Temporada.objects.filter(id=t_id, immoble=instance).update(
                    nom=t_data['nom'],
                    data_inici=t_data['data_inici'],
                    data_fi=t_data['data_fi'],
                    preu_nit=t_data['preu_nit'],
                    min_nits=t_data.get('min_nits', 1),
                    dies_checkin=t_data.get('dies_checkin', []),
                )
            else:
                Temporada.objects.create(
                    immoble=instance,
                    **t_data
                )

        return instance
