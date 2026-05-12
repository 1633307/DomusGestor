from django.db import migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):
    """
    La migració 0007 es va aplicar quan el camp es deia 'dia_checkin' i era
    de tipus integer. Posteriorment el codi va canviar a 'dies_checkin' (ArrayField).
    Aquesta migració sincronitza la BD (rename + canvi de tipus) sense tocar l'estat Django.
    """

    dependencies = [
        ('properties', '0007_temporada_min_nits_dia_checkin'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE properties_temporada
                            RENAME COLUMN dia_checkin TO dies_checkin;
                        ALTER TABLE properties_temporada
                            ALTER COLUMN dies_checkin TYPE integer[]
                            USING ARRAY[]::integer[];
                        UPDATE properties_temporada
                            SET dies_checkin = ARRAY[]::integer[]
                            WHERE dies_checkin IS NULL;
                    """,
                    reverse_sql="""
                        ALTER TABLE properties_temporada
                            ALTER COLUMN dies_checkin TYPE integer
                            USING NULL;
                        ALTER TABLE properties_temporada
                            RENAME COLUMN dies_checkin TO dia_checkin;
                    """,
                ),
            ],
            state_operations=[],
        ),
    ]
