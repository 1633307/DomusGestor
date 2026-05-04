from django.db import migrations
from django.db.models import Q


def set_descompte_individual_aplicat(apps, schema_editor):
    ReservaBasica = apps.get_model('bookings', 'ReservaBasica')
    ReservaBasica.objects.filter(
        Q(descompte_individual_percentatge__gt=0) |
        ~Q(descompte_individual_motiu='')
    ).update(descompte_individual_aplicat=True)


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_rename_cupo_to_descompte_individual'),
    ]

    operations = [
        migrations.RunPython(set_descompte_individual_aplicat, migrations.RunPython.noop),
    ]
