from django.db import migrations
from core.fields import hmac_value


def migrar_dades(apps, schema_editor):
    InquiliBasic = apps.get_model('bookings', 'InquiliBasic')
    Persona = apps.get_model('bookings', 'Persona')
    PerfilInquili = apps.get_model('bookings', 'PerfilInquili')
    PerfilPropietari = apps.get_model('bookings', 'PerfilPropietari')
    ReservaBasica = apps.get_model('bookings', 'ReservaBasica')
    Hoste = apps.get_model('bookings', 'Hoste')
    Immoble = apps.get_model('properties', 'Immoble')

    inquili_to_persona = {}

    for inquili in InquiliBasic.objects.all():
        persona = Persona.objects.create(
            nom_complet=inquili.nom_complet,
            genere=inquili.genere,
            tipus_document=inquili.tipus_document,
            dni_passaport=inquili.dni_passaport,
            dni_passaport_hash=inquili.dni_passaport_hash,
            nacionalitat=inquili.nacionalitat,
            data_naixement=inquili.data_naixement,
            residencia=inquili.residencia,
            email=inquili.email,
            telefon=inquili.telefon,
        )
        PerfilInquili.objects.create(persona=persona)

        if any([inquili.nom_fiscal, inquili.nif_cif, inquili.adreca_facturacio]):
            PerfilPropietari.objects.create(
                persona=persona,
                nom_fiscal=inquili.nom_fiscal,
                nif_cif=inquili.nif_cif,
                adreca_facturacio=inquili.adreca_facturacio,
                codi_postal_facturacio=inquili.codi_postal_facturacio,
                ciutat_facturacio=inquili.ciutat_facturacio,
                provincia_facturacio=inquili.provincia_facturacio,
                pais_facturacio=inquili.pais_facturacio,
                email_facturacio=inquili.email_facturacio,
                telefon_facturacio=inquili.telefon_facturacio,
                observacions_facturacio=inquili.observacions_facturacio,
                dades_facturacio=inquili.dades_facturacio or '',
            )

        inquili_to_persona[inquili.pk] = persona

    for reserva in ReservaBasica.objects.all():
        persona = inquili_to_persona.get(reserva.inquili_id)
        if persona:
            ReservaBasica.objects.filter(pk=reserva.pk).update(inquili_nou_id=persona.pk)

    for hoste in Hoste.objects.exclude(email=''):
        persona = Persona.objects.filter(email=hoste.email).first()
        if persona:
            Hoste.objects.filter(pk=hoste.pk).update(persona_id=persona.pk)

    for immoble in Immoble.objects.filter(propietari_id__isnull=True).exclude(propietari_nom=''):
        persona = None

        if immoble.propietari_email:
            persona = Persona.objects.filter(email=immoble.propietari_email).first()

        if persona is None and immoble.propietari_dni:
            persona = Persona.objects.filter(dni_passaport=immoble.propietari_dni).first()

        if persona is None:
            persona = Persona.objects.create(
                nom_complet=immoble.propietari_nom,
                dni_passaport=immoble.propietari_dni or '',
                dni_passaport_hash=hmac_value(immoble.propietari_dni) if immoble.propietari_dni else None,
                email=immoble.propietari_email or '',
                telefon=immoble.propietari_telefon or '',
            )

        if not PerfilPropietari.objects.filter(persona_id=persona.pk).exists():
            PerfilPropietari.objects.create(
                persona=persona,
                adreca_facturacio=immoble.propietari_adreca or '',
                iban=immoble.propietari_iban or '',
            )

        Immoble.objects.filter(pk=immoble.pk).update(propietari_id=persona.pk)


def revertir_dades(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0011_persona_perfilinquili_perfilpropietari'),
        ('properties', '0003_immoble_propietari'),
    ]

    operations = [
        migrations.RunPython(migrar_dades, revertir_dades),
    ]
