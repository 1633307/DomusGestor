from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_reservabasica_codi_cupo_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservabasica',
            old_name='codi_cupo',
            new_name='descompte_individual_motiu',
        ),
        migrations.RenameField(
            model_name='reservabasica',
            old_name='percentatge_cupo',
            new_name='descompte_individual_percentatge',
        ),
        migrations.AlterField(
            model_name='reservabasica',
            name='descompte_individual_motiu',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='reservabasica',
            name='descompte_individual_aplicat',
            field=models.BooleanField(default=False),
        ),
    ]
