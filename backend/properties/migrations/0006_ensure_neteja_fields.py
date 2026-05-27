from django.db import migrations


def ensure_neteja_fields(apps, schema_editor):
    """Add neteja columns if a previous no-op migration skipped them."""
    with schema_editor.connection.cursor() as cursor:
        columns = [
            ("neteja_tancament", "integer NOT NULL DEFAULT 0"),
            ("neteja_canvi", "integer NOT NULL DEFAULT 0"),
            ("neteja_obertura", "integer NOT NULL DEFAULT 0"),
        ]
        for col_name, col_def in columns:
            cursor.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = 'properties_immoble' "
                "AND column_name = %s",
                [col_name],
            )
            if cursor.fetchone():
                continue
            cursor.execute(
                f'ALTER TABLE "properties_immoble" '
                f'ADD COLUMN "{col_name}" {col_def}'
            )


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_immoble_neteja_fields'),
    ]

    operations = [
        migrations.RunPython(
            ensure_neteja_fields,
            migrations.RunPython.noop,
        ),
    ]
