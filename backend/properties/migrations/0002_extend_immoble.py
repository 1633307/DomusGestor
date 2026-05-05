from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='immoble',
            name='referencia',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='immoble',
            name='ciutat',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='immoble',
            name='codi_postal',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='immoble',
            name='tipus_immoble',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='immoble',
            name='foto_principal',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='immoble',
            name='propietari_nom',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='immoble',
            name='propietari_dni',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='immoble',
            name='propietari_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='immoble',
            name='propietari_telefon',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='immoble',
            name='propietari_adreca',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='immoble',
            name='propietari_iban',
            field=models.CharField(blank=True, default='', max_length=34),
        ),
        migrations.AlterField(
            model_name='immoble',
            name='metres_quadrats',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='immoble',
            name='num_habitacions',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='immoble',
            name='num_banys',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='immoble',
            name='capacitat_maxima',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='immoble',
            name='preu_base_nit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
