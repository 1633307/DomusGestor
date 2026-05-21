from rest_framework import serializers

from bookings.models import Persona
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
        extra_kwargs = {"immoble": {"required": False}}

    def validate_data_inici(self, value):
        return value.replace(year=2000)

    def validate_data_fi(self, value):
        return value.replace(year=2000)

    def validate_comissio(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("La comissio ha d'estar entre 0 i 100.")
        return value


class ImmobleSerializer(serializers.ModelSerializer):
    temporades = TemporadaSerializer(many=True, required=False)
    propietari_nom = serializers.CharField(
        source='propietari.nom_complet', read_only=True, default=None
    )
    propietari_email = serializers.EmailField(
        source='propietari.email', read_only=True, default=None
    )
    propietari_telefon = serializers.CharField(
        source='propietari.telefon', read_only=True, default=None
    )
    propietari_dni = serializers.CharField(
        source='propietari.dni_passaport', read_only=True, default=None
    )
    propietari_iban = serializers.SerializerMethodField()
    propietari_adreca = serializers.SerializerMethodField()

    class Meta:
        model = Immoble
        fields = [
            'id', 'nom_comercial', 'referencia', 'adreca', 'ciutat', 'codi_postal',
            'tipus_immoble', 'metres_quadrats', 'num_habitacions', 'num_banys',
            'capacitat_maxima', 'descripcio', 'preu_base_nit', 'descompte_actiu',
            'descompte_percentatge', 'fotos',
            'propietari', 'propietari_nom', 'propietari_email', 'propietari_telefon',
            'propietari_dni', 'propietari_iban', 'propietari_adreca',
            'hora_checkin_inici', 'hora_checkin_fi', 'hora_checkout_inici', 'hora_checkout_fi',
            'serveis', 'temporades', 'actiu', 'data_registre',
        ]
        read_only_fields = ['id', 'data_registre']

    def get_propietari_iban(self, obj):
        if obj.propietari and hasattr(obj.propietari, 'perfil_propietari'):
            return obj.propietari.perfil_propietari.iban
        return None

    def get_propietari_adreca(self, obj):
        if obj.propietari and hasattr(obj.propietari, 'perfil_propietari'):
            return obj.propietari.perfil_propietari.adreca_facturacio
        return None

    def validate_descompte_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descompte ha d'estar entre 0 i 100.")
        return value

    def validate(self, attrs):
        temporades = attrs.get('temporades', [])
        sorted_temps = sorted(temporades, key=lambda t: t['data_inici'])
        for i in range(len(sorted_temps) - 1):
            a = sorted_temps[i]
            b = sorted_temps[i + 1]
            if a['data_fi'] >= b['data_inici']:
                raise serializers.ValidationError({
                    'temporades': f"Les temporades '{a['nom']}' i '{b['nom']}' es solapen."
                })
        return attrs

    def update(self, instance, validated_data):
        temporades_data = validated_data.pop('temporades', [])
        instance = super().update(instance, validated_data)
        incoming_ids = [t.get('id') for t in temporades_data if t.get('id')]
        Temporada.objects.filter(immoble=instance).exclude(id__in=incoming_ids).delete()
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
                    comissio=t_data.get('comissio', 15.00),
                )
            else:
                Temporada.objects.create(immoble=instance, **t_data)
        return instance
