import re

from django.db import migrations


def is_hmac_hash(value):
    return len(value) == 64 and bool(re.fullmatch(r'[0-9a-f]{64}', value))


def fix_dni_passaport_hash_en_plain(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT to_regclass('bookings_persona')"
        )
        if cursor.fetchone()[0] is None:
            return
        cursor.execute(
            "SELECT id, dni_passaport FROM bookings_persona WHERE dni_passaport != ''"
        )
        rows = cursor.fetchall()
        for persona_id, dni_passaport in rows:
            if is_hmac_hash(dni_passaport):
                cursor.execute(
                    "UPDATE bookings_persona SET dni_passaport = '', dni_passaport_hash = NULL WHERE id = %s",
                    [persona_id],
                )


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_reservabasica_limpieza_extra'),
        ('bookings', '0006_set_descompte_individual_aplicat'),
    ]

    operations = [
        migrations.RunPython(
            fix_dni_passaport_hash_en_plain,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
