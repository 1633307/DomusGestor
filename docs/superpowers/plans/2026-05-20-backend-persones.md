# Reestructuració Backend de Persones - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir `InquiliBasic` per un model `Persona` unificat amb sub-perfils `PerfilInquili` i `PerfilPropietari`, i vincular `Immoble` a `Persona` via FK en lloc de camps incrustats.

**Architecture:** Nous models `Persona`, `PerfilInquili`, `PerfilPropietari` a l'app `bookings`. `ReservaBasica.inquili` passa a FK de `Persona`. `Hoste` afegeix una FK opcional a `Persona`. `Immoble` substitueix els camps `propietari_*` per una FK a `Persona`. Migració en 3 fases: esquema nou → dades → neteja.

**Tech Stack:** Django 5.0, PostgreSQL, Django REST Framework, `core.fields.EncryptedTextField` + `hmac_value` per a xifrat i unicitat de DNI.

---

## Mapa de fitxers

| Fitxer | Acció |
|--------|-------|
| `backend/bookings/models.py` | Modificar: afegir nous models, actualitzar Hoste + ReservaBasica, eliminar InquiliBasic |
| `backend/bookings/serializers.py` | Modificar: nous serialitzadors, eliminar InquiliSerializer, actualitzar Reserva + Pagament |
| `backend/bookings/views.py` | Modificar: nous PersonaListCreateView/DetailView, eliminar InquiliListCreateView/DetailView |
| `backend/bookings/urls.py` | Modificar: rutes persones/, eliminar inquilins/ |
| `backend/bookings/admin.py` | Modificar: registrar Persona, eliminar InquiliBasic |
| `backend/bookings/migrations/0011_persona_perfilinquili_perfilpropietari.py` | Crear (auto-generat) |
| `backend/bookings/migrations/0012_data_migrar_inquilibasic.py` | Crear (manual) |
| `backend/bookings/migrations/0013_cleanup_inquilibasic.py` | Crear (manual) |
| `backend/properties/models.py` | Modificar: afegir propietari FK, eliminar propietari_* |
| `backend/properties/serializers.py` | Modificar: camps del nou propietari FK |
| `backend/properties/migrations/0003_immoble_propietari.py` | Crear (auto-generat) |
| `backend/properties/migrations/0004_cleanup_propietari_fields.py` | Crear (auto-generat) |
| `backend/bookings/tests/__init__.py` | Crear (buit) |
| `backend/bookings/tests/test_persones.py` | Crear |

---

## Task 1: Nous models Persona/PerfilInquili/PerfilPropietari + migració esquema 0011

**Files:**
- Create: `backend/bookings/tests/__init__.py`
- Create: `backend/bookings/tests/test_persones.py`
- Modify: `backend/bookings/models.py`
- Create: `backend/bookings/migrations/0011_persona_perfilinquili_perfilpropietari.py` (auto)

- [ ] **Step 1.1: Crea el directori de tests i l'arxiu buit**

```
backend/bookings/tests/__init__.py   (fitxer buit)
```

- [ ] **Step 1.2: Escriu els tests per als nous models (han de fallar)**

Crea `backend/bookings/tests/test_persones.py`:

```python
from django.test import TestCase
from users.models import Usuari
from bookings.models import Persona, PerfilInquili, PerfilPropietari


class PersonaModelTest(TestCase):
    def test_crear_persona_basica(self):
        p = Persona.objects.create(nom_complet='Anna Garcia', email='anna@test.com')
        self.assertEqual(str(p), 'Anna Garcia')
        self.assertIsNone(p.dni_passaport_hash)

    def test_dni_hash_es_calcula_al_guardar(self):
        p = Persona.objects.create(nom_complet='Joan', dni_passaport='12345678A')
        self.assertIsNotNone(p.dni_passaport_hash)
        self.assertEqual(len(p.dni_passaport_hash), 64)

    def test_dni_hash_buit_si_no_hi_ha_dni(self):
        p = Persona.objects.create(nom_complet='Sense DNI')
        self.assertIsNone(p.dni_passaport_hash)

    def test_perfil_inquili_vincula_persona(self):
        p = Persona.objects.create(nom_complet='Llogater')
        pi = PerfilInquili.objects.create(persona=p)
        self.assertEqual(pi.persona, p)
        self.assertEqual(p.perfil_inquili, pi)

    def test_perfil_propietari_vincula_persona(self):
        p = Persona.objects.create(nom_complet='Propietari')
        pp = PerfilPropietari.objects.create(
            persona=p,
            nom_fiscal='Propietari SL',
            nif_cif='B12345678',
            iban='ES9121000418450200051332',
        )
        self.assertEqual(pp.persona, p)
        self.assertEqual(p.perfil_propietari, pp)

    def test_persona_pot_tenir_els_dos_perfils(self):
        p = Persona.objects.create(nom_complet='Dual')
        PerfilInquili.objects.create(persona=p)
        PerfilPropietari.objects.create(persona=p)
        self.assertTrue(hasattr(p, 'perfil_inquili'))
        self.assertTrue(hasattr(p, 'perfil_propietari'))
```

- [ ] **Step 1.3: Executa els tests per verificar que fallen**

```
cd backend && python manage.py test bookings.tests.test_persones -v 2
```

Resultat esperat: `ImportError` o `AttributeError` — Persona no existeix.

- [ ] **Step 1.4: Afegeix Persona, PerfilInquili, PerfilPropietari a models.py**

Afegeix a `backend/bookings/models.py` (entre els imports i `InquiliBasic`):

```python
GENERE_CHOICES = [
    ('Home', 'Home'),
    ('Dona', 'Dona'),
    ('Altres', 'Altres'),
]
DOCUMENT_CHOICES = [
    ('DNI', 'DNI'),
    ('NIE', 'NIE'),
    ('Passaport', 'Passaport'),
]


class Persona(models.Model):
    nom_complet = models.CharField(max_length=150)
    genere = models.CharField(max_length=10, choices=GENERE_CHOICES, blank=True, default='')
    tipus_document = models.CharField(max_length=15, choices=DOCUMENT_CHOICES, blank=True, default='')
    dni_passaport = models.TextField(blank=True, default='')
    dni_passaport_hash = models.CharField(
        max_length=64, unique=True, null=True, blank=True, editable=False, default=None
    )
    nacionalitat = models.CharField(max_length=80, blank=True, default='')
    data_naixement = models.DateField(null=True, blank=True)
    residencia = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, default='')
    telefon = models.CharField(max_length=30, blank=True, default='')

    def save(self, *args, **kwargs):
        if self.dni_passaport:
            self.dni_passaport_hash = hmac_value(self.dni_passaport)
        else:
            self.dni_passaport_hash = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Persones'
        ordering = ['nom_complet']

    def __str__(self):
        return self.nom_complet


class PerfilInquili(models.Model):
    persona = models.OneToOneField(
        Persona, on_delete=models.CASCADE, related_name='perfil_inquili'
    )

    class Meta:
        verbose_name = 'Perfil Inquilí'
        verbose_name_plural = 'Perfils Inquilins'

    def __str__(self):
        return f'Inquilí: {self.persona}'


class PerfilPropietari(models.Model):
    persona = models.OneToOneField(
        Persona, on_delete=models.CASCADE, related_name='perfil_propietari'
    )
    nom_fiscal = models.CharField(max_length=150, blank=True, default='')
    nif_cif = models.CharField(max_length=30, blank=True, default='')
    adreca_facturacio = models.TextField(blank=True, default='')
    codi_postal_facturacio = models.CharField(max_length=12, blank=True, default='')
    ciutat_facturacio = models.CharField(max_length=100, blank=True, default='')
    provincia_facturacio = models.CharField(max_length=100, blank=True, default='')
    pais_facturacio = models.CharField(max_length=100, blank=True, default='')
    email_facturacio = models.EmailField(blank=True, default='')
    telefon_facturacio = models.CharField(max_length=30, blank=True, default='')
    iban = models.CharField(max_length=34, blank=True, default='')
    observacions_facturacio = models.TextField(blank=True, default='')
    dades_facturacio = EncryptedTextField(blank=True)

    class Meta:
        verbose_name = 'Perfil Propietari'
        verbose_name_plural = 'Perfils Propietaris'

    def __str__(self):
        return f'Propietari: {self.persona}'
```

A més, afegeix `persona` FK a `Hoste` i `inquili_nou` a `ReservaBasica`. A `Hoste`, just **before** `class Meta`:

```python
    persona = models.ForeignKey(
        Persona, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hostes'
    )
```

A `ReservaBasica`, just **after** la línia `inquili = models.ForeignKey(InquiliBasic, ...)`:

```python
    inquili_nou = models.ForeignKey(
        Persona, on_delete=models.PROTECT,
        null=True, blank=True, related_name='reserves'
    )
```

- [ ] **Step 1.5: Genera la migració d'esquema**

```
cd backend && python manage.py makemigrations bookings --name persona_perfilinquili_perfilpropietari
```

Resultat esperat: `Migrations for 'bookings': backend/bookings/migrations/0011_persona_perfilinquili_perfilpropietari.py`

- [ ] **Step 1.6: Executa els tests — han de passar**

```
cd backend && python manage.py test bookings.tests.test_persones -v 2
```

Resultat esperat: `OK` (6 tests passed)

- [ ] **Step 1.7: Commit**

```bash
git add backend/bookings/models.py backend/bookings/migrations/0011_persona_perfilinquili_perfilpropietari.py backend/bookings/tests/
git commit -m "feat(bookings): afegir models Persona, PerfilInquili, PerfilPropietari i FKs transitionals"
```

---

## Task 2: Immoble.propietari FK + migració 0003 (properties)

**Files:**
- Modify: `backend/properties/models.py`
- Create: `backend/properties/migrations/0003_immoble_propietari.py` (auto)

- [ ] **Step 2.1: Escriu test per a Immoble.propietari**

Afegeix a `backend/bookings/tests/test_persones.py`:

```python
from properties.models import Immoble


class ImmoblePropietary(TestCase):
    def test_immoble_pot_tenir_propietari_nul(self):
        immoble = Immoble.objects.create(
            nom_comercial='Pis Test',
            adreca='Carrer Major 1',
            preu_base_nit=100,
        )
        self.assertIsNone(immoble.propietari)

    def test_immoble_vincula_persona_com_a_propietari(self):
        persona = Persona.objects.create(nom_complet='Propietari Test', email='prop@test.com')
        PerfilPropietari.objects.create(persona=persona)
        immoble = Immoble.objects.create(
            nom_comercial='Pis Test 2',
            adreca='Carrer Nou 5',
            preu_base_nit=80,
            propietari=persona,
        )
        self.assertEqual(immoble.propietari, persona)
        self.assertIn(immoble, persona.immobles.all())
```

- [ ] **Step 2.2: Executa el test — ha de fallar**

```
cd backend && python manage.py test bookings.tests.test_persones.ImmoblePropietary -v 2
```

Resultat esperat: `AttributeError: type object 'Immoble' has no attribute 'propietari'`

- [ ] **Step 2.3: Afegeix propietari FK a Immoble**

A `backend/properties/models.py`, afegeix l'import al capdamunt:

```python
# Nota: FK a Persona definida a bookings — usem string per evitar import circular
```

Afegeix el camp `propietari` a `Immoble`, just **before** `hora_checkin_inici`:

```python
    propietari = models.ForeignKey(
        'bookings.Persona',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='immobles',
    )
```

Deixa els camps `propietari_nom`, `propietari_dni`, etc. intactes de moment (s'eliminaran a Task 4).

- [ ] **Step 2.4: Genera la migració**

```
cd backend && python manage.py makemigrations properties --name immoble_propietari
```

Resultat esperat: `Migrations for 'properties': backend/properties/migrations/0003_immoble_propietari.py`

Verifica que la migració generada té `dependencies` que inclou `('bookings', '0011_persona_perfilinquili_perfilpropietari')`.

- [ ] **Step 2.5: Aplica les migracions**

```
cd backend && python manage.py migrate
```

Resultat esperat: `Applying bookings.0011... OK` i `Applying properties.0003... OK`

- [ ] **Step 2.6: Executa els tests — han de passar**

```
cd backend && python manage.py test bookings.tests.test_persones -v 2
```

Resultat esperat: `OK` (8 tests passed)

- [ ] **Step 2.7: Commit**

```bash
git add backend/properties/models.py backend/properties/migrations/0003_immoble_propietari.py
git commit -m "feat(properties): afegir Immoble.propietari FK a Persona"
```

---

## Task 3: Migració de dades (0012)

**Files:**
- Create: `backend/bookings/migrations/0012_data_migrar_inquilibasic.py`

- [ ] **Step 3.1: Escriu tests per validar la migració de dades**

Afegeix a `backend/bookings/tests/test_persones.py`:

```python
from django.test import TestCase
from bookings.models import InquiliBasic, Persona, PerfilInquili, PerfilPropietari, ReservaBasica
from properties.models import Immoble


class DataMigrationTest(TestCase):
    """Testa la lògica de migració de dades de forma independent."""

    def _run_migrar(self, apps_mock=None):
        """Executa la funció de migració directament sobre les dades de test."""
        from bookings.migrations.migration_helpers import migrar_inquilins_a_persones
        migrar_inquilins_a_persones()

    def test_inquilibasic_es_migra_a_persona(self):
        InquiliBasic.objects.create(
            nom_complet='Test User',
            email='test@test.com',
            telefon='600000000',
        )
        from bookings.migrations.migration_helpers import migrar_inquilins_a_persones
        migrar_inquilins_a_persones()
        self.assertEqual(Persona.objects.filter(email='test@test.com').count(), 1)
        p = Persona.objects.get(email='test@test.com')
        self.assertTrue(hasattr(p, 'perfil_inquili'))

    def test_inquili_amb_dades_fiscals_crea_perfil_propietari(self):
        InquiliBasic.objects.create(
            nom_complet='Fiscal User',
            email='fiscal@test.com',
            nom_fiscal='Fiscal SL',
            nif_cif='B99999999',
        )
        from bookings.migrations.migration_helpers import migrar_inquilins_a_persones
        migrar_inquilins_a_persones()
        p = Persona.objects.get(email='fiscal@test.com')
        self.assertTrue(hasattr(p, 'perfil_propietari'))
        self.assertEqual(p.perfil_propietari.nif_cif, 'B99999999')

    def test_reservabasica_inquili_nou_s_assigna(self):
        inquili = InquiliBasic.objects.create(
            nom_complet='Reserva User',
            email='reserva@test.com',
        )
        immoble = Immoble.objects.create(
            nom_comercial='Pis Migr', adreca='C/ Test 1', preu_base_nit=50
        )
        reserva = ReservaBasica.objects.create(
            immoble=immoble,
            inquili=inquili,
            data_entrada='2026-06-01',
            data_sortida='2026-06-05',
        )
        from bookings.migrations.migration_helpers import migrar_inquilins_a_persones
        migrar_inquilins_a_persones()
        reserva.refresh_from_db()
        self.assertIsNotNone(reserva.inquili_nou)
        self.assertEqual(reserva.inquili_nou.email, 'reserva@test.com')
```

- [ ] **Step 3.2: Crea el mòdul d'helpers de migració**

Crea `backend/bookings/migrations/migration_helpers.py`:

```python
"""
Funcions de migració de dades reutilitzables per a tests.
Operen directament sobre els models Django (no sobre models històrics).
"""
from bookings.models import InquiliBasic, Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste
from properties.models import Immoble
from core.fields import hmac_value


def migrar_inquilins_a_persones():
    """
    Migra cada InquiliBasic a Persona + PerfilInquili.
    Si té dades fiscals, crea també PerfilPropietari.
    Actualitza ReservaBasica.inquili_nou i Hoste.persona.
    """
    inquili_to_persona = {}

    for inquili in InquiliBasic.objects.all():
        persona = Persona.objects.create(
            nom_complet=inquili.nom_complet,
            genere=inquili.genere,
            tipus_document=inquili.tipus_document,
            dni_passaport=inquili.dni_passaport,
            dni_passaport_hash=inquili.dni_passaport_hash,
            nacionalitat=inquili.nacionalitat,
            data_naixement=inquili.data_naixement,
            residencia=inquili.residencia,
            email=inquili.email,
            telefon=inquili.telefon,
        )
        PerfilInquili.objects.create(persona=persona)

        if any([inquili.nom_fiscal, inquili.nif_cif, inquili.adreca_facturacio]):
            PerfilPropietari.objects.create(
                persona=persona,
                nom_fiscal=inquili.nom_fiscal,
                nif_cif=inquili.nif_cif,
                adreca_facturacio=inquili.adreca_facturacio,
                codi_postal_facturacio=inquili.codi_postal_facturacio,
                ciutat_facturacio=inquili.ciutat_facturacio,
                provincia_facturacio=inquili.provincia_facturacio,
                pais_facturacio=inquili.pais_facturacio,
                email_facturacio=inquili.email_facturacio,
                telefon_facturacio=inquili.telefon_facturacio,
                observacions_facturacio=inquili.observacions_facturacio,
                dades_facturacio=inquili.dades_facturacio or '',
            )

        inquili_to_persona[inquili.pk] = persona

    for reserva in ReservaBasica.objects.all():
        persona = inquili_to_persona.get(reserva.inquili_id)
        if persona:
            ReservaBasica.objects.filter(pk=reserva.pk).update(inquili_nou=persona)

    for hoste in Hoste.objects.filter(email__isnull=False).exclude(email=''):
        persona = Persona.objects.filter(email=hoste.email).first()
        if persona:
            Hoste.objects.filter(pk=hoste.pk).update(persona=persona)


def migrar_propietaris_immobles():
    """
    Migra els camps propietari_* de cada Immoble a Persona + PerfilPropietari.
    Deduplicació: cerca primer per email, després per DNI.
    """
    for immoble in Immoble.objects.filter(propietari__isnull=True).exclude(propietari_nom=''):
        persona = None

        if immoble.propietari_email:
            persona = Persona.objects.filter(email=immoble.propietari_email).first()

        if persona is None and immoble.propietari_dni:
            persona = Persona.objects.filter(dni_passaport=immoble.propietari_dni).first()

        if persona is None:
            persona = Persona.objects.create(
                nom_complet=immoble.propietari_nom,
                dni_passaport=immoble.propietari_dni or '',
                dni_passaport_hash=hmac_value(immoble.propietari_dni) if immoble.propietari_dni else None,
                email=immoble.propietari_email or '',
                telefon=immoble.propietari_telefon or '',
            )

        if not PerfilPropietari.objects.filter(persona=persona).exists():
            PerfilPropietari.objects.create(
                persona=persona,
                adreca_facturacio=immoble.propietari_adreca or '',
                iban=immoble.propietari_iban or '',
            )

        Immoble.objects.filter(pk=immoble.pk).update(propietari=persona)
```

- [ ] **Step 3.3: Executa els tests d'helpers — han de passar**

```
cd backend && python manage.py test bookings.tests.test_persones.DataMigrationTest -v 2
```

Resultat esperat: `OK` (3 tests passed)

- [ ] **Step 3.4: Crea la migració de dades formal**

Crea `backend/bookings/migrations/0012_data_migrar_inquilibasic.py`:

```python
from django.db import migrations
from core.fields import hmac_value


def migrar_dades(apps, schema_editor):
    InquiliBasic = apps.get_model('bookings', 'InquiliBasic')
    Persona = apps.get_model('bookings', 'Persona')
    PerfilInquili = apps.get_model('bookings', 'PerfilInquili')
    PerfilPropietari = apps.get_model('bookings', 'PerfilPropietari')
    ReservaBasica = apps.get_model('bookings', 'ReservaBasica')
    Hoste = apps.get_model('bookings', 'Hoste')
    Immoble = apps.get_model('properties', 'Immoble')

    inquili_to_persona = {}

    for inquili in InquiliBasic.objects.all():
        persona = Persona.objects.create(
            nom_complet=inquili.nom_complet,
            genere=inquili.genere,
            tipus_document=inquili.tipus_document,
            dni_passaport=inquili.dni_passaport,
            dni_passaport_hash=inquili.dni_passaport_hash,
            nacionalitat=inquili.nacionalitat,
            data_naixement=inquili.data_naixement,
            residencia=inquili.residencia,
            email=inquili.email,
            telefon=inquili.telefon,
        )
        PerfilInquili.objects.create(persona=persona)

        if any([inquili.nom_fiscal, inquili.nif_cif, inquili.adreca_facturacio]):
            PerfilPropietari.objects.create(
                persona=persona,
                nom_fiscal=inquili.nom_fiscal,
                nif_cif=inquili.nif_cif,
                adreca_facturacio=inquili.adreca_facturacio,
                codi_postal_facturacio=inquili.codi_postal_facturacio,
                ciutat_facturacio=inquili.ciutat_facturacio,
                provincia_facturacio=inquili.provincia_facturacio,
                pais_facturacio=inquili.pais_facturacio,
                email_facturacio=inquili.email_facturacio,
                telefon_facturacio=inquili.telefon_facturacio,
                observacions_facturacio=inquili.observacions_facturacio,
                dades_facturacio=inquili.dades_facturacio or '',
            )

        inquili_to_persona[inquili.pk] = persona

    for reserva in ReservaBasica.objects.all():
        persona = inquili_to_persona.get(reserva.inquili_id)
        if persona:
            ReservaBasica.objects.filter(pk=reserva.pk).update(inquili_nou_id=persona.pk)

    for hoste in Hoste.objects.exclude(email=''):
        persona = Persona.objects.filter(email=hoste.email).first()
        if persona:
            Hoste.objects.filter(pk=hoste.pk).update(persona_id=persona.pk)

    for immoble in Immoble.objects.filter(propietari_id__isnull=True).exclude(propietari_nom=''):
        persona = None

        if immoble.propietari_email:
            persona = Persona.objects.filter(email=immoble.propietari_email).first()

        if persona is None and immoble.propietari_dni:
            persona = Persona.objects.filter(dni_passaport=immoble.propietari_dni).first()

        if persona is None:
            persona = Persona.objects.create(
                nom_complet=immoble.propietari_nom,
                dni_passaport=immoble.propietari_dni or '',
                dni_passaport_hash=hmac_value(immoble.propietari_dni) if immoble.propietari_dni else None,
                email=immoble.propietari_email or '',
                telefon=immoble.propietari_telefon or '',
            )

        if not PerfilPropietari.objects.filter(persona_id=persona.pk).exists():
            PerfilPropietari.objects.create(
                persona=persona,
                adreca_facturacio=immoble.propietari_adreca or '',
                iban=immoble.propietari_iban or '',
            )

        Immoble.objects.filter(pk=immoble.pk).update(propietari_id=persona.pk)


def revertir_dades(apps, schema_editor):
    # No reversible — dades noves ja no existien a InquiliBasic
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0011_persona_perfilinquili_perfilpropietari'),
        ('properties', '0003_immoble_propietari'),
    ]

    operations = [
        migrations.RunPython(migrar_dades, revertir_dades),
    ]
```

- [ ] **Step 3.5: Aplica la migració de dades**

```
cd backend && python manage.py migrate
```

Resultat esperat: `Applying bookings.0012... OK`

- [ ] **Step 3.6: Verifica manualment que les dades s'han migrat**

```
cd backend && python manage.py shell -c "
from bookings.models import Persona, PerfilInquili
print('Persones:', Persona.objects.count())
print('PerfilInquili:', PerfilInquili.objects.count())
"
```

Resultat esperat: els mateixos comptadors que `InquiliBasic` tenia.

- [ ] **Step 3.7: Commit**

```bash
git add backend/bookings/migrations/0012_data_migrar_inquilibasic.py backend/bookings/migrations/migration_helpers.py backend/bookings/tests/test_persones.py
git commit -m "feat(bookings): migració de dades InquiliBasic → Persona + PerfilInquili/Propietari"
```

---

## Task 4: Neteja d'esquema — eliminar InquiliBasic i camps propietari_*

**Files:**
- Modify: `backend/bookings/models.py`
- Modify: `backend/properties/models.py`
- Create: `backend/bookings/migrations/0013_cleanup_inquilibasic.py` (manual)
- Create: `backend/properties/migrations/0004_cleanup_propietari_fields.py` (auto)

- [ ] **Step 4.1: Elimina InquiliBasic i simplifica models.py bookings**

Reemplaça tot el contingut de `backend/bookings/models.py` amb la versió final:

```python
from django.db import models

from core.fields import EncryptedTextField, hmac_value
from properties.models import Immoble

GENERE_CHOICES = [
    ('Home', 'Home'),
    ('Dona', 'Dona'),
    ('Altres', 'Altres'),
]
DOCUMENT_CHOICES = [
    ('DNI', 'DNI'),
    ('NIE', 'NIE'),
    ('Passaport', 'Passaport'),
]


class Persona(models.Model):
    nom_complet = models.CharField(max_length=150)
    genere = models.CharField(max_length=10, choices=GENERE_CHOICES, blank=True, default='')
    tipus_document = models.CharField(max_length=15, choices=DOCUMENT_CHOICES, blank=True, default='')
    dni_passaport = models.TextField(blank=True, default='')
    dni_passaport_hash = models.CharField(
        max_length=64, unique=True, null=True, blank=True, editable=False, default=None
    )
    nacionalitat = models.CharField(max_length=80, blank=True, default='')
    data_naixement = models.DateField(null=True, blank=True)
    residencia = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, default='')
    telefon = models.CharField(max_length=30, blank=True, default='')

    def save(self, *args, **kwargs):
        if self.dni_passaport:
            self.dni_passaport_hash = hmac_value(self.dni_passaport)
        else:
            self.dni_passaport_hash = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Persones'
        ordering = ['nom_complet']

    def __str__(self):
        return self.nom_complet


class PerfilInquili(models.Model):
    persona = models.OneToOneField(
        Persona, on_delete=models.CASCADE, related_name='perfil_inquili'
    )

    class Meta:
        verbose_name = 'Perfil Inquilí'
        verbose_name_plural = 'Perfils Inquilins'

    def __str__(self):
        return f'Inquilí: {self.persona}'


class PerfilPropietari(models.Model):
    persona = models.OneToOneField(
        Persona, on_delete=models.CASCADE, related_name='perfil_propietari'
    )
    nom_fiscal = models.CharField(max_length=150, blank=True, default='')
    nif_cif = models.CharField(max_length=30, blank=True, default='')
    adreca_facturacio = models.TextField(blank=True, default='')
    codi_postal_facturacio = models.CharField(max_length=12, blank=True, default='')
    ciutat_facturacio = models.CharField(max_length=100, blank=True, default='')
    provincia_facturacio = models.CharField(max_length=100, blank=True, default='')
    pais_facturacio = models.CharField(max_length=100, blank=True, default='')
    email_facturacio = models.EmailField(blank=True, default='')
    telefon_facturacio = models.CharField(max_length=30, blank=True, default='')
    iban = models.CharField(max_length=34, blank=True, default='')
    observacions_facturacio = models.TextField(blank=True, default='')
    dades_facturacio = EncryptedTextField(blank=True)

    class Meta:
        verbose_name = 'Perfil Propietari'
        verbose_name_plural = 'Perfils Propietaris'

    def __str__(self):
        return f'Propietari: {self.persona}'


class ReservaBasica(models.Model):
    TIPUS_CHOICES = [
        ('Airbnb', 'Airbnb'),
        ('Booking', 'Booking'),
        ('Direct', 'Directa'),
        ('Altres', 'Altres'),
    ]
    ESTAT_RESERVA_CHOICES = [
        ('prereservada', 'Prereservada'),
        ('reservada', 'Reservada'),
        ('lista', 'Lista'),
        ('cancelada', 'Cancelada'),
    ]

    immoble = models.ForeignKey(Immoble, on_delete=models.CASCADE, related_name='reserves')
    inquili = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='reserves')
    data_entrada = models.DateField()
    data_sortida = models.DateField()
    pagat = models.BooleanField(default=False)

    codi_reserva = models.CharField(max_length=30, blank=True, default='')
    tipus_reserva = models.CharField(max_length=20, choices=TIPUS_CHOICES, blank=True, default='')
    estat_reserva = models.CharField(
        max_length=20, choices=ESTAT_RESERVA_CHOICES, blank=True, null=True, default=None,
    )
    net = models.BooleanField(default=False)
    comentaris_interns = models.TextField(blank=True, default='')
    num_hostes = models.PositiveIntegerField(default=0)
    descompte_immoble_aplicat = models.BooleanField(default=False)
    descompte_immoble_percentatge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descompte_individual_aplicat = models.BooleanField(default=False)
    descompte_individual_percentatge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descompte_individual_motiu = models.TextField(blank=True, default='')

    ESTAT_PAGAMENT_CHOICES = [
        ('pendent', 'Pendent'),
        ('parcial', 'Parcial'),
        ('pagada', 'Pagada'),
        ('retornada', 'Retornada'),
        ('rebutjada', 'Rebutjada'),
    ]
    estat_pagament = models.CharField(
        max_length=20, choices=ESTAT_PAGAMENT_CHOICES, default='pendent'
    )
    import_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    import_pagat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    import_pendent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fianca = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metode_pagament = models.CharField(max_length=50, blank=True, default='')
    data_ultim_pagament = models.DateField(null=True, blank=True)
    observacions_pagament = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reserves'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.codi_reserva:
            entrada = self.data_entrada
            year = entrada.year if hasattr(entrada, 'year') else str(entrada)[:4]
            self.codi_reserva = f"RES-{year}-{self.id:04d}"
            ReservaBasica.objects.filter(pk=self.pk).update(codi_reserva=self.codi_reserva)

    def __str__(self):
        return f"Reserva {self.codi_reserva or self.id}: {self.immoble.nom_comercial}"


class PagamentReserva(models.Model):
    METODE_CHOICES = [
        ('efectiu', 'Efectiu'),
        ('transferencia', 'Transferència'),
        ('targeta', 'Targeta'),
        ('bizum', 'Bizum'),
        ('altres', 'Altres'),
    ]
    ESTAT_CHOICES = [
        ('pendent', 'Pendent'),
        ('pagat', 'Pagat'),
        ('cancelat', 'Cancel·lat'),
    ]
    reserva = models.ForeignKey(ReservaBasica, on_delete=models.CASCADE, related_name='pagaments')
    data_pagament = models.DateField()
    import_pagament = models.DecimalField(max_digits=10, decimal_places=2)
    metode_pagament = models.CharField(max_length=20, choices=METODE_CHOICES, default='transferencia')
    estat = models.CharField(max_length=20, choices=ESTAT_CHOICES, default='pendent')

    class Meta:
        verbose_name = 'Pagament'
        verbose_name_plural = 'Pagaments'
        ordering = ['-data_pagament']

    def __str__(self):
        return f"{self.import_pagament}€ · {self.reserva.codi_reserva} ({self.estat})"


class Hoste(models.Model):
    reserva = models.ForeignKey(
        ReservaBasica, on_delete=models.CASCADE, related_name='hostes'
    )
    persona = models.ForeignKey(
        Persona, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hostes'
    )
    es_principal = models.BooleanField(default=False)

    nom_complet = models.CharField(max_length=150)
    genere = models.CharField(max_length=10, choices=GENERE_CHOICES, blank=True, default='')
    relacio_parental = models.CharField(max_length=30, blank=True, default='')
    tipus_document = models.CharField(max_length=15, choices=DOCUMENT_CHOICES, blank=True, default='')
    numero_document = models.CharField(max_length=30, blank=True, default='')
    nacionalitat = models.CharField(max_length=80, blank=True, default='')
    data_naixement = models.DateField(null=True, blank=True)
    residencia = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, default='')
    telefon = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        verbose_name = 'Hoste'
        verbose_name_plural = 'Hostes'
        ordering = ['-es_principal', 'id']

    def __str__(self):
        prefix = 'Principal' if self.es_principal else 'Hoste'
        return f"{prefix}: {self.nom_complet}"


class Comunicacio(models.Model):
    CANAL_CHOICES = [
        ('Email', 'Email'),
        ('Telefon', 'Telèfon'),
        ('WhatsApp', 'WhatsApp'),
        ('Sistema', 'Sistema'),
    ]
    ESTAT_CHOICES = [
        ('enviada', 'Enviada'),
        ('pendent', 'Pendent'),
        ('error', 'Error'),
        ('programada', 'Programada'),
    ]
    reserva = models.ForeignKey(
        ReservaBasica, on_delete=models.CASCADE, related_name='comunicacions'
    )
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)
    titol = models.CharField(max_length=200)
    destinatari = models.CharField(max_length=200, blank=True, default='')
    data = models.DateField(null=True, blank=True)
    estat = models.CharField(max_length=20, choices=ESTAT_CHOICES, default='pendent')
    resum = models.TextField(blank=True, default='')
    creat_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comunicació'
        verbose_name_plural = 'Comunicacions'
        ordering = ['-creat_el']

    def __str__(self):
        return f"{self.canal}: {self.titol}"
```

- [ ] **Step 4.2: Elimina propietari_* d'Immoble**

A `backend/properties/models.py`, elimina aquests 6 camps de la classe `Immoble`:

```python
# Elimina:
propietari_nom = models.CharField(max_length=150, blank=True, default='')
propietari_dni = models.CharField(max_length=20, blank=True, default='')
propietari_email = models.EmailField(blank=True, default='')
propietari_telefon = models.CharField(max_length=30, blank=True, default='')
propietari_adreca = models.TextField(blank=True, default='')
propietari_iban = models.CharField(max_length=34, blank=True, default='')
```

- [ ] **Step 4.3: Genera la migració de cleanup de properties**

```
cd backend && python manage.py makemigrations properties --name cleanup_propietari_fields
```

Resultat esperat: `Migrations for 'properties': backend/properties/migrations/0004_cleanup_propietari_fields.py`

- [ ] **Step 4.4: Escriu la migració de cleanup de bookings manualment**

Crea `backend/bookings/migrations/0013_cleanup_inquilibasic.py`:

```python
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0012_data_migrar_inquilibasic'),
        ('properties', '0004_cleanup_propietari_fields'),
    ]

    operations = [
        # Pas 1: fer inquili_nou NOT NULL
        migrations.AlterField(
            model_name='reservabasica',
            name='inquili_nou',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reserves_nou',
                to='bookings.persona',
            ),
        ),
        # Pas 2: eliminar l'antiga FK a InquiliBasic
        migrations.RemoveField(
            model_name='reservabasica',
            name='inquili',
        ),
        # Pas 3: reanomenar inquili_nou → inquili
        migrations.RenameField(
            model_name='reservabasica',
            old_name='inquili_nou',
            new_name='inquili',
        ),
        # Pas 4: corregir related_name a 'reserves'
        migrations.AlterField(
            model_name='reservabasica',
            name='inquili',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reserves',
                to='bookings.persona',
            ),
        ),
        # Pas 5: eliminar el model InquiliBasic
        migrations.DeleteModel(
            name='InquiliBasic',
        ),
    ]
```

- [ ] **Step 4.5: Aplica totes les migracions de cleanup**

```
cd backend && python manage.py migrate
```

Resultat esperat: `Applying bookings.0013... OK` i `Applying properties.0004... OK`

- [ ] **Step 4.6: Elimina migration_helpers.py i els DataMigrationTest (ja no compilaran sense InquiliBasic)**

Elimina `backend/bookings/migrations/migration_helpers.py`.

A `backend/bookings/tests/test_persones.py`, elimina tota la classe `DataMigrationTest` i els imports `InquiliBasic`, `ReservaBasica` (si no s'usen en altres tests).

- [ ] **Step 4.7: Executa tots els tests existents**

```
cd backend && python manage.py test bookings.tests -v 2
```

Resultat esperat: `OK` (tots els tests passats sense errors d'import de InquiliBasic)

- [ ] **Step 4.8: Commit**

```bash
git rm backend/bookings/migrations/migration_helpers.py
git add backend/bookings/models.py backend/properties/models.py \
        backend/bookings/migrations/0013_cleanup_inquilibasic.py \
        backend/properties/migrations/0004_cleanup_propietari_fields.py \
        backend/bookings/tests/test_persones.py
git commit -m "feat: neteja d'esquema — eliminar InquiliBasic i propietari_* d'Immoble"
```

---

## Task 5: Serialitzadors

**Files:**
- Modify: `backend/bookings/serializers.py`
- Modify: `backend/properties/serializers.py`

- [ ] **Step 5.1: Escriu tests per a PersonaSerializer**

Afegeix a `backend/bookings/tests/test_persones.py`:

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import Usuari


class PersonaAPITest(APITestCase):
    def setUp(self):
        self.user = Usuari.objects.create_user(
            nip='0001', username='testuser',
            email='user@test.com', password='pass1234'
        )
        self.client.force_authenticate(user=self.user)

    def test_crear_persona_via_api(self):
        url = reverse('persona-list')
        resp = self.client.post(url, {
            'nom_complet': 'Nova Persona',
            'email': 'nova@test.com',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['nom_complet'], 'Nova Persona')
        self.assertIsNone(resp.data['perfil_inquili'])
        self.assertIsNone(resp.data['perfil_propietari'])

    def test_llistar_persones(self):
        Persona.objects.create(nom_complet='Persona 1', email='p1@test.com')
        Persona.objects.create(nom_complet='Persona 2', email='p2@test.com')
        url = reverse('persona-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_detall_persona_inclou_perfils(self):
        p = Persona.objects.create(nom_complet='Amb Perfils', email='perfils@test.com')
        PerfilInquili.objects.create(persona=p)
        PerfilPropietari.objects.create(persona=p, iban='ES9121000418450200051332')
        url = reverse('persona-detail', args=[p.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data['perfil_inquili'])
        self.assertIsNotNone(resp.data['perfil_propietari'])
        self.assertEqual(resp.data['perfil_propietari']['iban'], 'ES9121000418450200051332')

    def test_dni_duplicat_retorna_error(self):
        Persona.objects.create(nom_complet='Primer', dni_passaport='12345678A')
        url = reverse('persona-list')
        resp = self.client.post(url, {
            'nom_complet': 'Segon',
            'dni_passaport': '12345678A',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dni_passaport', resp.data)

    def test_eliminar_persona(self):
        p = Persona.objects.create(nom_complet='A Eliminar', email='del@test.com')
        url = reverse('persona-detail', args=[p.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Persona.objects.filter(pk=p.pk).exists())
```

- [ ] **Step 5.2: Executa els tests d'API — han de fallar**

```
cd backend && python manage.py test bookings.tests.test_persones.PersonaAPITest -v 2
```

Resultat esperat: `NoReverseMatch` o `AttributeError` — endpoints no existeixen.

- [ ] **Step 5.3: Reemplaça bookings/serializers.py**

```python
from django.db import transaction
from rest_framework import serializers

from core.fields import hmac_value
from properties.models import Immoble

from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste, Comunicacio, PagamentReserva


def _has_value(value):
    return value is not None and value != ''


def _can_use_document_for_persona(persona, document):
    if not document:
        return False
    document_hash = hmac_value(document)
    return not (
        Persona.objects
        .filter(dni_passaport_hash=document_hash)
        .exclude(pk=persona.pk)
        .exists()
    )


def sync_persona_from_hoste(persona, hoste, overwrite=False):
    if persona is None or hoste is None:
        return []

    changed_fields = []
    field_map = [
        ('nom_complet', 'nom_complet'),
        ('genere', 'genere'),
        ('tipus_document', 'tipus_document'),
        ('nacionalitat', 'nacionalitat'),
        ('data_naixement', 'data_naixement'),
        ('residencia', 'residencia'),
        ('email', 'email'),
        ('telefon', 'telefon'),
    ]

    for hoste_field, persona_field in field_map:
        source_value = getattr(hoste, hoste_field, None)
        current_value = getattr(persona, persona_field, None)
        if _has_value(source_value) and (overwrite or not _has_value(current_value)):
            setattr(persona, persona_field, source_value)
            changed_fields.append(persona_field)

    if _has_value(getattr(hoste, 'numero_document', None)):
        current_document = getattr(persona, 'dni_passaport', None)
        if (overwrite or not _has_value(current_document)) and _can_use_document_for_persona(
            persona, hoste.numero_document,
        ):
            persona.dni_passaport = hoste.numero_document
            changed_fields.append('dni_passaport')

    if changed_fields:
        update_fields = sorted(set(changed_fields + ['dni_passaport_hash']))
        persona.save(update_fields=update_fields)

    return changed_fields


class PerfilInquiliSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilInquili
        fields = ['id']


class PerfilPropietariSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilPropietari
        fields = [
            'id', 'nom_fiscal', 'nif_cif', 'adreca_facturacio',
            'codi_postal_facturacio', 'ciutat_facturacio', 'provincia_facturacio',
            'pais_facturacio', 'email_facturacio', 'telefon_facturacio',
            'iban', 'observacions_facturacio',
        ]


class PersonaSerializer(serializers.ModelSerializer):
    perfil_inquili = PerfilInquiliSerializer(read_only=True)
    perfil_propietari = PerfilPropietariSerializer(read_only=True)
    reserves = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = [
            'id', 'nom_complet', 'genere', 'tipus_document', 'dni_passaport',
            'nacionalitat', 'data_naixement', 'residencia', 'email', 'telefon',
            'perfil_inquili', 'perfil_propietari', 'reserves',
        ]
        read_only_fields = ['id']

    def validate_dni_passaport(self, value):
        if not value:
            return value
        h = hmac_value(value)
        qs = Persona.objects.filter(dni_passaport_hash=h)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ja existeix una persona amb aquest DNI/Passaport.")
        return value

    def to_internal_value(self, data):
        cleaned = dict(data)
        if cleaned.get('data_naixement') in ('', None):
            cleaned['data_naixement'] = None
        return super().to_internal_value(cleaned)

    def get_reserves(self, obj):
        return [
            {
                'id': r.id,
                'codi_reserva': r.codi_reserva,
                'immoble_nom': r.immoble.nom_comercial,
                'data_entrada': str(r.data_entrada),
                'data_sortida': str(r.data_sortida),
                'estat_reserva': r.estat_reserva,
            }
            for r in obj.reserves.select_related('immoble').all()
        ]


class HosteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hoste
        fields = [
            'id', 'es_principal', 'nom_complet', 'genere', 'relacio_parental',
            'tipus_document', 'numero_document', 'nacionalitat',
            'data_naixement', 'residencia', 'email', 'telefon',
        ]
        read_only_fields = ['id']

    def to_internal_value(self, data):
        cleaned = dict(data)
        if cleaned.get('data_naixement') in ('', None):
            cleaned['data_naixement'] = None
        return super().to_internal_value(cleaned)


class ReservaSerializer(serializers.ModelSerializer):
    immoble_nom = serializers.CharField(source='immoble.nom_comercial', read_only=True)
    inquili_nom = serializers.CharField(source='inquili.nom_complet', read_only=True)
    hostes = HosteSerializer(many=True, required=False)

    class Meta:
        model = ReservaBasica
        fields = [
            'id', 'immoble', 'immoble_nom', 'inquili', 'inquili_nom',
            'data_entrada', 'data_sortida', 'pagat',
            'codi_reserva', 'tipus_reserva', 'estat_reserva', 'net',
            'comentaris_interns', 'num_hostes',
            'descompte_immoble_aplicat', 'descompte_immoble_percentatge',
            'descompte_individual_aplicat', 'descompte_individual_percentatge',
            'descompte_individual_motiu',
            'estat_pagament', 'import_total', 'import_pagat', 'import_pendent',
            'fianca', 'metode_pagament', 'data_ultim_pagament',
            'observacions_pagament',
            'hostes',
        ]
        read_only_fields = ['id', 'codi_reserva']

    def validate_descompte_immoble_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descompte de l'immoble ha d'estar entre 0 i 100.")
        return value

    def validate_descompte_individual_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descompte individual ha d'estar entre 0 i 100.")
        return value

    def _replace_hostes(self, reserva, hostes_data):
        reserva.hostes.all().delete()
        principal_assigned = False
        new_hostes = []
        for h_data in hostes_data:
            es_principal = bool(h_data.get('es_principal'))
            if es_principal and principal_assigned:
                es_principal = False
            if es_principal:
                principal_assigned = True
            payload = {**h_data, 'es_principal': es_principal, 'reserva': reserva}
            new_hostes.append(Hoste(**payload))
        if new_hostes and not principal_assigned:
            new_hostes[0].es_principal = True
        for h in new_hostes:
            h.save()

    def _sync_persona_from_principal_hoste(self, reserva):
        hoste_principal = reserva.hostes.filter(es_principal=True).first()
        sync_persona_from_hoste(reserva.inquili, hoste_principal, overwrite=False)

    @transaction.atomic
    def create(self, validated_data):
        hostes_data = validated_data.pop('hostes', [])
        reserva = ReservaBasica.objects.create(**validated_data)
        if hostes_data:
            self._replace_hostes(reserva, hostes_data)
            reserva.num_hostes = len(hostes_data)
            reserva.save(update_fields=['num_hostes'])
        self._sync_persona_from_principal_hoste(reserva)
        return reserva

    @transaction.atomic
    def update(self, instance, validated_data):
        hostes_data = validated_data.pop('hostes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if hostes_data is not None:
            self._replace_hostes(instance, hostes_data)
            instance.num_hostes = len(hostes_data)
            instance.save(update_fields=['num_hostes'])
        self._sync_persona_from_principal_hoste(instance)
        return instance


class ComunicacioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunicacio
        fields = [
            'id', 'reserva', 'canal', 'titol', 'destinatari',
            'data', 'estat', 'resum', 'creat_el',
        ]
        read_only_fields = ['id', 'creat_el', 'reserva']

    def to_internal_value(self, data):
        cleaned = dict(data)
        if cleaned.get('data') in ('', None):
            cleaned['data'] = None
        return super().to_internal_value(cleaned)


class PagamentReservaSerializer(serializers.ModelSerializer):
    codi_reserva = serializers.CharField(source='reserva.codi_reserva', read_only=True)
    inquili_nom = serializers.CharField(source='reserva.inquili.nom_complet', read_only=True)

    class Meta:
        model = PagamentReserva
        fields = [
            'id', 'reserva', 'codi_reserva', 'inquili_nom',
            'data_pagament', 'import_pagament', 'metode_pagament', 'estat',
        ]
        read_only_fields = ['id']


class DashboardSerializer(serializers.Serializer):
    total_reserves = serializers.IntegerField()
    total_immobles = serializers.IntegerField()
    total_inquilins = serializers.IntegerField()
    immobles_actius = serializers.IntegerField()
    reserves_pagades = serializers.IntegerField()
```

- [ ] **Step 5.4: Actualitza properties/serializers.py**

Reemplaça `backend/properties/serializers.py`:

```python
from rest_framework import serializers

from bookings.models import Persona
from .models import Immoble, Servei, Temporada


class ServeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servei
        fields = '__all__'


class TemporadaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Temporada
        fields = '__all__'
        extra_kwargs = {"immoble": {"required": False}}

    def validate_data_inici(self, value):
        return value.replace(year=2000)

    def validate_data_fi(self, value):
        return value.replace(year=2000)

    def validate_comissio(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("La comissio ha d'estar entre 0 i 100.")
        return value


class ImmobleSerializer(serializers.ModelSerializer):
    temporades = TemporadaSerializer(many=True, required=False)
    propietari_nom = serializers.CharField(
        source='propietari.nom_complet', read_only=True, default=None
    )
    propietari_email = serializers.EmailField(
        source='propietari.email', read_only=True, default=None
    )
    propietari_telefon = serializers.CharField(
        source='propietari.telefon', read_only=True, default=None
    )
    propietari_dni = serializers.CharField(
        source='propietari.dni_passaport', read_only=True, default=None
    )
    propietari_iban = serializers.SerializerMethodField()
    propietari_adreca = serializers.SerializerMethodField()

    class Meta:
        model = Immoble
        fields = [
            'id', 'nom_comercial', 'referencia', 'adreca', 'ciutat', 'codi_postal',
            'tipus_immoble', 'metres_quadrats', 'num_habitacions', 'num_banys',
            'capacitat_maxima', 'descripcio', 'preu_base_nit', 'descompte_actiu',
            'descompte_percentatge', 'fotos',
            'propietari', 'propietari_nom', 'propietari_email', 'propietari_telefon',
            'propietari_dni', 'propietari_iban', 'propietari_adreca',
            'hora_checkin_inici', 'hora_checkin_fi', 'hora_checkout_inici', 'hora_checkout_fi',
            'serveis', 'temporades', 'actiu', 'data_registre',
        ]
        read_only_fields = ['id', 'data_registre']

    def get_propietari_iban(self, obj):
        if obj.propietari and hasattr(obj.propietari, 'perfil_propietari'):
            return obj.propietari.perfil_propietari.iban
        return None

    def get_propietari_adreca(self, obj):
        if obj.propietari and hasattr(obj.propietari, 'perfil_propietari'):
            return obj.propietari.perfil_propietari.adreca_facturacio
        return None

    def validate_descompte_percentatge(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descompte ha d'estar entre 0 i 100.")
        return value

    def validate(self, attrs):
        temporades = attrs.get('temporades', [])
        sorted_temps = sorted(temporades, key=lambda t: t['data_inici'])
        for i in range(len(sorted_temps) - 1):
            a = sorted_temps[i]
            b = sorted_temps[i + 1]
            if a['data_fi'] >= b['data_inici']:
                raise serializers.ValidationError({
                    'temporades': f"Les temporades '{a['nom']}' i '{b['nom']}' es solapen."
                })
        return attrs

    def update(self, instance, validated_data):
        temporades_data = validated_data.pop('temporades', [])
        instance = super().update(instance, validated_data)
        incoming_ids = [t.get('id') for t in temporades_data if t.get('id')]
        Temporada.objects.filter(immoble=instance).exclude(id__in=incoming_ids).delete()
        for t_data in temporades_data:
            t_id = t_data.get('id')
            if t_id:
                Temporada.objects.filter(id=t_id, immoble=instance).update(
                    nom=t_data['nom'],
                    data_inici=t_data['data_inici'],
                    data_fi=t_data['data_fi'],
                    preu_nit=t_data['preu_nit'],
                    min_nits=t_data.get('min_nits', 1),
                    dies_checkin=t_data.get('dies_checkin', []),
                    comissio=t_data.get('comissio', 15.00),
                )
            else:
                Temporada.objects.create(immoble=instance, **t_data)
        return instance
```

- [ ] **Step 5.5: Executa els tests de serialitzadors — han de fallar per falta de views/URLs**

```
cd backend && python manage.py test bookings.tests.test_persones.PersonaAPITest -v 2
```

Resultat esperat: `NoReverseMatch: Reverse for 'persona-list' not found`

- [ ] **Step 5.6: Commit parcial de serialitzadors**

```bash
git add backend/bookings/serializers.py backend/properties/serializers.py
git commit -m "feat(bookings): nous serialitzadors Persona/PerfilInquili/PerfilPropietari, eliminar InquiliSerializer"
```

---

## Task 6: Views, URLs i Admin

**Files:**
- Modify: `backend/bookings/views.py`
- Modify: `backend/bookings/urls.py`
- Modify: `backend/bookings/admin.py`

- [ ] **Step 6.1: Reemplaça bookings/views.py**

```python
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.models import Immoble

from .models import Persona, PerfilInquili, ReservaBasica, Comunicacio
from .serializers import (
    PersonaSerializer, ReservaSerializer, ComunicacioSerializer, DashboardSerializer,
)
from .services import calcular_preview_reserva


class PersonaListCreateView(generics.ListCreateAPIView):
    queryset = Persona.objects.all().order_by('nom_complet')
    serializer_class = PersonaSerializer


class PersonaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Persona.objects
        .select_related('perfil_inquili', 'perfil_propietari')
        .prefetch_related('reserves__immoble')
        .all()
    )
    serializer_class = PersonaSerializer


class ReservaListCreateView(generics.ListCreateAPIView):
    queryset = (
        ReservaBasica.objects
        .select_related('immoble', 'inquili')
        .prefetch_related('hostes')
        .all()
    )
    serializer_class = ReservaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        filtro_reserva = self.request.query_params.get('reserva')
        if filtro_reserva:
            queryset = queryset.filter(id=filtro_reserva)
        filtro_immoble = self.request.query_params.get('immoble')
        if filtro_immoble:
            queryset = queryset.filter(immoble_id=filtro_immoble)
        filtro_inquili = self.request.query_params.get('inquili')
        if filtro_inquili:
            queryset = queryset.filter(inquili_id=filtro_inquili)
        return queryset


class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        ReservaBasica.objects
        .select_related('immoble', 'inquili')
        .prefetch_related('hostes')
        .all()
    )
    serializer_class = ReservaSerializer


class ComunicacioListCreateView(generics.ListCreateAPIView):
    serializer_class = ComunicacioSerializer

    def get_queryset(self):
        return Comunicacio.objects.filter(reserva_id=self.kwargs['reserva_pk'])

    def perform_create(self, serializer):
        serializer.save(reserva_id=self.kwargs['reserva_pk'])


class ComunicacioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComunicacioSerializer

    def get_queryset(self):
        return Comunicacio.objects.filter(reserva_id=self.kwargs['reserva_pk'])


class ReservaPreviewView(APIView):
    def post(self, request):
        return Response(calcular_preview_reserva(request.data))


class DashboardView(APIView):
    def get(self, request):
        data = {
            'total_reserves': ReservaBasica.objects.count(),
            'total_immobles': Immoble.objects.count(),
            'total_inquilins': PerfilInquili.objects.count(),
            'immobles_actius': Immoble.objects.filter(actiu=True).count(),
            'reserves_pagades': ReservaBasica.objects.filter(pagat=True).count(),
        }
        return Response(DashboardSerializer(data).data)
```

- [ ] **Step 6.2: Actualitza bookings/urls.py**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('persones/', views.PersonaListCreateView.as_view(), name='persona-list'),
    path('persones/<int:pk>/', views.PersonaDetailView.as_view(), name='persona-detail'),
    path('reserves/', views.ReservaListCreateView.as_view(), name='reserva-list'),
    path('reserves/preview/', views.ReservaPreviewView.as_view(), name='reserva-preview'),
    path('reserves/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva-detail'),
    path(
        'reserves/<int:reserva_pk>/comunicacions/',
        views.ComunicacioListCreateView.as_view(),
        name='comunicacio-list',
    ),
    path(
        'reserves/<int:reserva_pk>/comunicacions/<int:pk>/',
        views.ComunicacioDetailView.as_view(),
        name='comunicacio-detail',
    ),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
```

- [ ] **Step 6.3: Actualitza bookings/admin.py**

```python
from django.contrib import admin

from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste, Comunicacio


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'email', 'telefon', 'nacionalitat', 'es_inquili', 'es_propietari']
    search_fields = ['nom_complet', 'email', 'telefon', 'dni_passaport']

    @admin.display(boolean=True)
    def es_inquili(self, obj):
        return hasattr(obj, 'perfil_inquili')

    @admin.display(boolean=True)
    def es_propietari(self, obj):
        return hasattr(obj, 'perfil_propietari')


@admin.register(PerfilPropietari)
class PerfilPropietariAdmin(admin.ModelAdmin):
    list_display = ['persona', 'nom_fiscal', 'nif_cif', 'iban']
    search_fields = ['persona__nom_complet', 'nom_fiscal', 'nif_cif']


class HosteInline(admin.TabularInline):
    model = Hoste
    extra = 0
    fields = ['es_principal', 'nom_complet', 'tipus_document', 'numero_document', 'email']


class ComunicacioInline(admin.TabularInline):
    model = Comunicacio
    extra = 0
    fields = ['canal', 'titol', 'destinatari', 'data', 'estat']


@admin.register(ReservaBasica)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'codi_reserva', 'immoble', 'inquili',
        'data_entrada', 'data_sortida', 'pagat', 'estat_pagament',
    ]
    list_filter = ['pagat', 'tipus_reserva', 'estat_pagament']
    search_fields = ['codi_reserva']
    inlines = [HosteInline, ComunicacioInline]


@admin.register(Hoste)
class HosteAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'reserva', 'es_principal', 'tipus_document']
    list_filter = ['es_principal', 'tipus_document']
    search_fields = ['nom_complet', 'email']


@admin.register(Comunicacio)
class ComunicacioAdmin(admin.ModelAdmin):
    list_display = ['titol', 'reserva', 'canal', 'estat', 'data', 'creat_el']
    list_filter = ['canal', 'estat']
    search_fields = ['titol', 'destinatari']
```

- [ ] **Step 6.4: Executa tots els tests — han de passar**

```
cd backend && python manage.py test bookings.tests -v 2
```

Resultat esperat: `OK` — tots els tests passats incloent `PersonaAPITest`.

- [ ] **Step 6.5: Commit**

```bash
git add backend/bookings/views.py backend/bookings/urls.py backend/bookings/admin.py
git commit -m "feat(bookings): views i URLs per a Persona, eliminar endpoints inquilins"
```

---

## Task 7: Verificació final i test de regressió

- [ ] **Step 7.1: Verifica que el servidor arrenca sense errors**

```
cd backend && python manage.py check
```

Resultat esperat: `System check identified no issues (0 silenced).`

- [ ] **Step 7.2: Executa la suite de tests completa**

```
cd backend && python manage.py test bookings properties -v 2
```

Resultat esperat: Tots els tests passen, cap import a `InquiliBasic`.

- [ ] **Step 7.3: Verifica que el migration graph és consistent**

```
cd backend && python manage.py migrate --check
```

Resultat esperat: cap migració pendent.

- [ ] **Step 7.4: Commit final**

```bash
git add -A
git commit -m "feat: reestructuració backend persones — Persona/PerfilInquili/PerfilPropietari completada"
```

---

## Notes per al sub-projecte 2 (frontend)

El frontend actual usa `/api/bookings/inquilins/` que **ja no existeix**. Fins que s'implementi el sub-projecte 2:
- `InfoInmoblePage` envia camps `propietari_nom`, `propietari_dni`, etc. com a write — ara el serialitzador els ignora. El `propietari` FK cal enviar-lo com a ID.
- `PersonesPage` i `InfoPersonaPage` han d'apuntar a `/api/bookings/persones/`.
- `api.js`: `inquilinsApi` cal canviar-lo per `personesApi` apuntant a `/bookings/persones/`.
