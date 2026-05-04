from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_immoble_fotos'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temporada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('data_inici', models.DateField()),
                ('data_fi', models.DateField()),
                ('preu_nit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('immoble', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='temporades',
                    to='properties.immoble',
                )),
            ],
            options={
                'verbose_name_plural': 'Temporades',
                'ordering': ['data_inici'],
            },
        ),
    ]
