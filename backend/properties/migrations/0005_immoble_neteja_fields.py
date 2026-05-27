from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_cleanup_propietari_fields'),
    ]

    operations = [
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
    ]
