import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_temporada'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporada',
            name='min_nits',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='temporada',
            name='dies_checkin',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
