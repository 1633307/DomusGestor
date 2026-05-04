from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_immoble_descompte_actiu_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servei',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('icona', models.CharField(blank=True, default='', max_length=50)),
                ('categoria', models.CharField(
                    choices=[
                        ('climatitzacio',    'Climatització'),
                        ('conectivitat',     'Connectivitat'),
                        ('electrodomestics', 'Electrodomèstics'),
                        ('exterior',         'Exterior'),
                        ('altres',           'Altres'),
                    ],
                    default='altres',
                    max_length=20,
                )),
            ],
            options={
                'verbose_name_plural': 'Serveis',
                'ordering': ['categoria', 'nom'],
            },
        ),
        migrations.AddField(
            model_name='immoble',
            name='serveis',
            field=models.ManyToManyField(blank=True, related_name='immobles', to='properties.servei'),
        ),
    ]
