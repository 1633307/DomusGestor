import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0014_fix_dni_passaport_hash_en_plain'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComunicacioEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipus', models.CharField(choices=[
                    ('prereservada_inquili',    'Pre-reserva → Inquilí'),
                    ('prereservada_propietari', 'Pre-reserva → Propietari'),
                    ('confirmada_inquili',      'Confirmada → Inquilí'),
                    ('confirmada_propietari',   'Confirmada → Propietari'),
                    ('cancelada_inquili',       'Cancel·lada → Inquilí'),
                    ('cancelada_propietari',    'Cancel·lada → Propietari'),
                    ('pagament_inquili',        'Pagament → Inquilí'),
                    ('pagament_propietari',     'Pagament → Propietari'),
                    ('manual',                  'Manual'),
                ], max_length=30)),
                ('destinatari', models.EmailField(blank=True, default='', max_length=254)),
                ('assumpte', models.CharField(max_length=200)),
                ('enviat_a', models.DateTimeField(auto_now_add=True)),
                ('exit', models.BooleanField()),
                ('error_msg', models.TextField(blank=True, default='')),
                ('enviat_per', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
                ('reserva', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='emails_enviats',
                    to='bookings.reservabasica',
                )),
            ],
            options={
                'verbose_name': 'Email enviat',
                'verbose_name_plural': 'Emails enviats',
                'ordering': ['-enviat_a'],
            },
        ),
    ]
