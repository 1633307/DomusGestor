from django.db import migrations, models


def add_neteja_fields_if_missing(apps, schema_editor):
    """Add neteja columns only if they don't already exist."""
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
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='immoble',
                    name='neteja_tancament',
                    field=models.PositiveIntegerField(default=0),
                ),
                migrations.AddField(
                    model_name='immoble',
                    name='neteja_canvi',
                    field=models.PositiveIntegerField(default=0),
                ),
                migrations.AddField(
                    model_name='immoble',
                    name='neteja_obertura',
                    field=models.PositiveIntegerField(default=0),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    add_neteja_fields_if_missing,
                    migrations.RunPython.noop,
                ),
            ],
        ),
    ]
