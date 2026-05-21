from django.db import migrations, models


def decrypt_dni_passaports(apps, schema_editor):
    from core.fields import decrypt_value
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, dni_passaport FROM bookings_inquilibasic "
            "WHERE dni_passaport IS NOT NULL AND dni_passaport != ''"
        )
        rows = cursor.fetchall()
        for row_id, encrypted_val in rows:
            if encrypted_val:
                decrypted = decrypt_value(encrypted_val)
                cursor.execute(
                    "UPDATE bookings_inquilibasic SET dni_passaport = %s WHERE id = %s",
                    [decrypted, row_id],
                )


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0008_alter_inquilibasic_options_and_more'),
    ]

    operations = [
        migrations.RunPython(decrypt_dni_passaports, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='inquilibasic',
            name='dni_passaport',
            field=models.TextField(blank=True, default=''),
        ),
    ]
