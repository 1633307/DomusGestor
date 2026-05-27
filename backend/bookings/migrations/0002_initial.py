import django.db.models.deletion
from django.db import migrations, models


def add_fk_if_missing(apps, schema_editor):
    """Add FK columns only if they don't already exist (idempotent)."""
    with schema_editor.connection.cursor() as cursor:
        fk_columns = [
            ("bookings_reservabasica", "immoble_id", "properties_immoble", "CASCADE"),
            ("bookings_reservabasica", "inquili_id", "bookings_persona", "RESTRICT"),
            ("bookings_pagamentreserva", "reserva_id", "bookings_reservabasica", "CASCADE"),
            ("bookings_hoste", "reserva_id", "bookings_reservabasica", "CASCADE"),
            ("bookings_comunicacio", "reserva_id", "bookings_reservabasica", "CASCADE"),
        ]
        for table, column, ref_table, on_delete in fk_columns:
            cursor.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = %s AND column_name = %s",
                [table, column],
            )
            if cursor.fetchone():
                continue
            not_null = "NOT NULL" if on_delete != "SET NULL" else ""
            cursor.execute(
                f'ALTER TABLE "{table}" ADD COLUMN "{column}" bigint {not_null}'
            )
            constraint = f"fk_{table}_{column}"
            on_del_sql = f"ON DELETE {on_delete}"
            cursor.execute(
                f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint}" '
                f'FOREIGN KEY ("{column}") REFERENCES "{ref_table}" ("id") '
                f"{on_del_sql} DEFERRABLE INITIALLY DEFERRED"
            )
            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS "{table}_{column}_idx" '
                f'ON "{table}" ("{column}")'
            )


class Migration(migrations.Migration):

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
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='reserves',
                        to='properties.immoble',
                    ),
                ),
                migrations.AddField(
                    model_name='reservabasica',
                    name='inquili',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='reserves',
                        to='bookings.persona',
                    ),
                ),
                migrations.AddField(
                    model_name='pagamentreserva',
                    name='reserva',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='pagaments',
                        to='bookings.reservabasica',
                    ),
                ),
                migrations.AddField(
                    model_name='hoste',
                    name='reserva',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='hostes',
                        to='bookings.reservabasica',
                    ),
                ),
                migrations.AddField(
                    model_name='comunicacio',
                    name='reserva',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='comunicacions',
                        to='bookings.reservabasica',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(add_fk_if_missing, migrations.RunPython.noop),
            ],
        ),
    ]
