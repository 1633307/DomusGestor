from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0008_rename_dia_checkin_to_dies_checkin'),
    ]

    operations = [
        migrations.AddField(
            model_name='immoble',
            name='hora_checkin_inici',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='immoble',
            name='hora_checkin_fi',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='immoble',
            name='hora_checkout_inici',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='immoble',
            name='hora_checkout_fi',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
