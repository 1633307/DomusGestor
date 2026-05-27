from django.db import migrations, models


def add_limpieza_extra_if_missing(apps, schema_editor):
    """Add limpieza_extra column only if it doesn't already exist."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'bookings_reservabasica' "
            "AND column_name = 'limpieza_extra'"
        )
        if cursor.fetchone():
            return
        cursor.execute(
            'ALTER TABLE "bookings_reservabasica" '
            'ADD COLUMN "limpieza_extra" smallint NOT NULL DEFAULT 0'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='reservabasica',
                    name='limpieza_extra',
                    field=models.PositiveSmallIntegerField(default=0),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_limpieza_extra_if_missing,
                    migrations.RunPython.noop,
                ),
            ],
        ),
    ]
