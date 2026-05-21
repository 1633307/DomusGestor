from django.db import migrations, models


def decrypt_existing_documents(apps, schema_editor):
    from core.fields import decrypt_value

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, numero_document FROM bookings_hoste WHERE numero_document != ''"
        )
        rows = cursor.fetchall()
        for hoste_id, encrypted_value in rows:
            if encrypted_value:
                decrypted = decrypt_value(encrypted_value)
                cursor.execute(
                    "UPDATE bookings_hoste SET numero_document = %s WHERE id = %s",
                    [decrypted, hoste_id],
                )


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0009_decrypt_dni_passaport'),
    ]

    operations = [
        migrations.RunPython(decrypt_existing_documents, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='hoste',
            name='numero_document_hash',
        ),
        migrations.AlterField(
            model_name='hoste',
            name='numero_document',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
