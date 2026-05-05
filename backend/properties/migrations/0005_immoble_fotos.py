from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_servei_immoble_serveis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='immoble',
            name='foto_principal',
        ),
        migrations.AddField(
            model_name='immoble',
            name='fotos',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=500),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
