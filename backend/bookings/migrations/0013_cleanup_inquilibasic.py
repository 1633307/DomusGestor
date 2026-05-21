import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0012_data_migrar_inquilibasic'),
        ('properties', '0004_cleanup_propietari_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservabasica',
            name='inquili_nou',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reserves_nou',
                to='bookings.persona',
            ),
        ),
        migrations.RemoveField(
            model_name='reservabasica',
            name='inquili',
        ),
        migrations.RenameField(
            model_name='reservabasica',
            old_name='inquili_nou',
            new_name='inquili',
        ),
        migrations.AlterField(
            model_name='reservabasica',
            name='inquili',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reserves',
                to='bookings.persona',
            ),
        ),
        migrations.DeleteModel(
            name='InquiliBasic',
        ),
    ]
