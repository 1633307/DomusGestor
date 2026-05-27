from django.db import migrations


def _column_exists(cursor, table, column):
    cursor.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = %s AND column_name = %s",
        [table, column],
    )
    return cursor.fetchone() is not None


def ensure_fk_columns(apps, schema_editor):
    """Add FK columns if 0002_initial ran as a no-op."""
    with schema_editor.connection.cursor() as cursor:
        fk_columns = [
            ("bookings_reservabasica", "immoble_id", "properties_immoble", "CASCADE"),
            ("bookings_reservabasica", "inquili_id", "bookings_persona", "RESTRICT"),
            ("bookings_pagamentreserva", "reserva_id", "bookings_reservabasica", "CASCADE"),
            ("bookings_hoste", "reserva_id", "bookings_reservabasica", "CASCADE"),
            ("bookings_comunicacio", "reserva_id", "bookings_reservabasica", "CASCADE"),
        ]
        for table, column, ref_table, on_delete in fk_columns:
            if _column_exists(cursor, table, column):
                continue
            not_null = "NOT NULL" if on_delete != "SET NULL" else ""
            cursor.execute(
                f'ALTER TABLE "{table}" ADD COLUMN "{column}" bigint {not_null}'
            )
            constraint = f"fk_{table}_{column}"
            cursor.execute(
                f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint}" '
                f'FOREIGN KEY ("{column}") REFERENCES "{ref_table}" ("id") '
                f'ON DELETE {on_delete} DEFERRABLE INITIALLY DEFERRED'
            )
            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS "{table}_{column}_idx" '
                f'ON "{table}" ("{column}")'
            )


def ensure_limpieza_extra(apps, schema_editor):
    """Add limpieza_extra column if 0003 ran as a no-op."""
    with schema_editor.connection.cursor() as cursor:
        if _column_exists(cursor, "bookings_reservabasica", "limpieza_extra"):
            return
        cursor.execute(
            'ALTER TABLE "bookings_reservabasica" '
            'ADD COLUMN "limpieza_extra" smallint NOT NULL DEFAULT 0'
        )


def ensure_comunicacio_email_table(apps, schema_editor):
    """Create ComunicacioEmail table if 0015 ran as a no-op."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('bookings_comunicacioemail')")
        if cursor.fetchone()[0] is not None:
            return
        cursor.execute('''
            CREATE TABLE "bookings_comunicacioemail" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "tipus" varchar(30) NOT NULL,
                "destinatari" varchar(254) NOT NULL DEFAULT '',
                "assumpte" varchar(200) NOT NULL,
                "enviat_a" timestamp with time zone NOT NULL DEFAULT NOW(),
                "exit" boolean NOT NULL,
                "error_msg" text NOT NULL DEFAULT '',
                "enviat_per_id" integer NULL,
                "reserva_id" bigint NOT NULL
            )
        ''')
        cursor.execute('''
            ALTER TABLE "bookings_comunicacioemail"
            ADD CONSTRAINT "fk_comunicacioemail_enviat_per"
            FOREIGN KEY ("enviat_per_id")
            REFERENCES "auth_user" ("id")
            ON DELETE SET NULL
            DEFERRABLE INITIALLY DEFERRED
        ''')
        cursor.execute('''
            ALTER TABLE "bookings_comunicacioemail"
            ADD CONSTRAINT "fk_comunicacioemail_reserva"
            FOREIGN KEY ("reserva_id")
            REFERENCES "bookings_reservabasica" ("id")
            ON DELETE CASCADE
            DEFERRABLE INITIALLY DEFERRED
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS "bookings_comunicacioemail_enviat_per_id_idx"
            ON "bookings_comunicacioemail" ("enviat_per_id")
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS "bookings_comunicacioemail_reserva_id_idx"
            ON "bookings_comunicacioemail" ("reserva_id")
        ''')


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0016_merge_20260526_1813'),
    ]

    operations = [
        migrations.RunPython(ensure_fk_columns, migrations.RunPython.noop),
        migrations.RunPython(ensure_limpieza_extra, migrations.RunPython.noop),
        migrations.RunPython(ensure_comunicacio_email_table, migrations.RunPython.noop),
    ]
