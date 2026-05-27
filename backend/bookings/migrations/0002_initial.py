import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    # Squashed: FK fields are now declared inline in 0001_initial CreateModel
    # operations. This migration uses SeparateDatabaseAndState so Django's
    # internal state knows about the FKs without touching the database
    # (the columns already exist from the original migration chain).

    initial = True

    dependencies = [
        ('bookings', '0001_initial'),
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='reservabasica',
                    name='immoble',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reserves', to='properties.immoble'),
                ),
                migrations.AddField(
                    model_name='reservabasica',
                    name='inquili',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reserves', to='bookings.persona'),
                ),
                migrations.AddField(
                    model_name='pagamentreserva',
                    name='reserva',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagaments', to='bookings.reservabasica'),
                ),
                migrations.AddField(
                    model_name='hoste',
                    name='reserva',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hostes', to='bookings.reservabasica'),
                ),
                migrations.AddField(
                    model_name='comunicacio',
                    name='reserva',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comunicacions', to='bookings.reservabasica'),
                ),
            ],
            database_operations=[],
        ),
    ]
