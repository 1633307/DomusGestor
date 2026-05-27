import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_comunicacio_email_if_missing(apps, schema_editor):
    """Create the ComunicacioEmail table only if it doesn't already exist."""
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
            CREATE INDEX "bookings_comunicacioemail_enviat_per_id_idx"
            ON "bookings_comunicacioemail" ("enviat_per_id")
        ''')
        cursor.execute('''
            CREATE INDEX "bookings_comunicacioemail_reserva_id_idx"
            ON "bookings_comunicacioemail" ("reserva_id")
        ''')


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0014_fix_dni_passaport_hash_en_plain'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ComunicacioEmail',
                    fields=[
                        ('id', models.BigAutoField(
                            auto_created=True, primary_key=True,
                            serialize=False, verbose_name='ID',
                        )),
                        ('tipus', models.CharField(choices=[
                            ('prereservada_inquili', 'Pre-reserva \u2192 Inquil\u00ed'),
                            ('prereservada_propietari', 'Pre-reserva \u2192 Propietari'),
                            ('confirmada_inquili', 'Confirmada \u2192 Inquil\u00ed'),
                            ('confirmada_propietari', 'Confirmada \u2192 Propietari'),
                            ('cancelada_inquili', 'Cancel\u00b7lada \u2192 Inquil\u00ed'),
                            ('cancelada_propietari', 'Cancel\u00b7lada \u2192 Propietari'),
                            ('pagament_inquili', 'Pagament \u2192 Inquil\u00ed'),
                            ('pagament_propietari', 'Pagament \u2192 Propietari'),
                            ('manual', 'Manual'),
                        ], max_length=30)),
                        ('destinatari', models.EmailField(
                            blank=True, default='', max_length=254,
                        )),
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
            ],
            database_operations=[
                migrations.RunPython(
                    create_comunicacio_email_if_missing,
                    migrations.RunPython.noop,
                ),
            ],
        ),
    ]
