from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_reservabasica_codi_reserva_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservabasica',
            name='estat_reserva',
            field=models.CharField(
                blank=True,
                choices=[
                    ('prereservada', 'Prereservada'),
                    ('reservada', 'Reservada'),
                    ('lista', 'Lista'),
                    ('cancelada', 'Cancelada'),
                ],
                default=None,
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='reservabasica',
            name='net',
            field=models.BooleanField(default=False),
        ),
    ]
