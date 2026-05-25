# Email Communications Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement automatic and manual email sending for DomusGestor reservations using Gmail SMTP and Django signals.

**Architecture:** Django signals detect state changes on `ReservaBasica` and `PagamentReserva`, triggering email sends via Gmail SMTP. Manual emails sent when a `Comunicacio` with `canal='Email'` is created via API. All sends logged to new `ComunicacioEmail` model. Signals use `transaction.on_commit` so emails fire after the full save (including `codi_reserva` update).

**Tech Stack:** Django built-in `send_mail`, Django signals (`pre_save`/`post_save`), `transaction.on_commit`, Django template engine, Gmail SMTP, `TransactionTestCase` for signal tests.

---

### Task 1: Gmail SMTP configuration

**Files:**
- Modify: `backend/domusgestor/settings.py`
- Modify: `backend/.env`

- [ ] **Step 1: Add EMAIL_* to end of settings.py**

```python
# Email (Gmail SMTP)
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='DomusGestor <>')
```

- [ ] **Step 2: Add placeholder variables to .env**

```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=DomusGestor <>
```

Note: `console.EmailBackend` prints emails to terminal. Change to `smtp.EmailBackend` and fill credentials when ready for real sending. Gmail requires an App Password (Google Account → Security → 2FA → App Passwords).

- [ ] **Step 3: Verify**

```bash
cd backend && python manage.py check
```
Expected: System check identified no issues (0 silenced).

- [ ] **Step 4: Commit**

```bash
git add backend/domusgestor/settings.py backend/.env
git commit -m "feat(email): add Gmail SMTP configuration"
```

---

### Task 2: ComunicacioEmail model + migration + admin

**Files:**
- Modify: `backend/bookings/models.py`
- Modify: `backend/bookings/admin.py`
- Create: `backend/bookings/tests/test_comunicacio_email.py`

- [ ] **Step 1: Write failing test**

Create `backend/bookings/tests/test_comunicacio_email.py`:

```python
from django.test import TestCase
from bookings.models import ComunicacioEmail, ReservaBasica, Persona
from properties.models import Immoble


def _make_reserva():
    persona = Persona.objects.create(nom_complet='Test', email='test@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='Carrer 1')
    return ReservaBasica.objects.create(
        immoble=immoble, inquili=persona,
        data_entrada='2026-07-01', data_sortida='2026-07-07',
    )


class ComunicacioEmailModelTest(TestCase):
    def test_crear_log_exit(self):
        reserva = _make_reserva()
        log = ComunicacioEmail.objects.create(
            reserva=reserva, tipus='prereservada_inquili',
            destinatari='test@test.com', assumpte='Test', exit=True,
        )
        self.assertTrue(log.exit)
        self.assertIsNone(log.enviat_per)
        self.assertEqual(log.error_msg, '')

    def test_crear_log_error(self):
        reserva = _make_reserva()
        log = ComunicacioEmail.objects.create(
            reserva=reserva, tipus='prereservada_inquili',
            destinatari='', assumpte='Test', exit=False, error_msg='Sense email',
        )
        self.assertFalse(log.exit)
        self.assertEqual(log.error_msg, 'Sense email')

    def test_str(self):
        reserva = _make_reserva()
        log = ComunicacioEmail.objects.create(
            reserva=reserva, tipus='confirmada_inquili',
            destinatari='a@b.com', assumpte='Confirmada', exit=True,
        )
        self.assertIn('confirmada_inquili', str(log))
```

- [ ] **Step 2: Run test — verify fail**

```bash
cd backend && python manage.py test bookings.tests.test_comunicacio_email -v 2
```
Expected: ImportError (ComunicacioEmail not defined).

- [ ] **Step 3: Add ComunicacioEmail to models.py after the Comunicacio class**

```python
class ComunicacioEmail(models.Model):
    TIPUS_CHOICES = [
        ('prereservada_inquili',    'Pre-reserva → Inquilí'),
        ('prereservada_propietari', 'Pre-reserva → Propietari'),
        ('confirmada_inquili',      'Confirmada → Inquilí'),
        ('confirmada_propietari',   'Confirmada → Propietari'),
        ('cancelada_inquili',       'Cancel·lada → Inquilí'),
        ('cancelada_propietari',    'Cancel·lada → Propietari'),
        ('pagament_inquili',        'Pagament → Inquilí'),
        ('pagament_propietari',     'Pagament → Propietari'),
        ('manual',                  'Manual'),
    ]
    reserva     = models.ForeignKey(
        ReservaBasica, on_delete=models.CASCADE, related_name='emails_enviats'
    )
    tipus       = models.CharField(max_length=30, choices=TIPUS_CHOICES)
    destinatari = models.EmailField(blank=True, default='')
    assumpte    = models.CharField(max_length=200)
    enviat_a    = models.DateTimeField(auto_now_add=True)
    enviat_per  = models.ForeignKey(
        'users.Usuari', on_delete=models.SET_NULL, null=True, blank=True
    )
    exit        = models.BooleanField()
    error_msg   = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Email enviat'
        verbose_name_plural = 'Emails enviats'
        ordering = ['-enviat_a']

    def __str__(self):
        return f"{self.tipus} → {self.destinatari} ({'OK' if self.exit else 'ERROR'})"
```

- [ ] **Step 4: Create and apply migration**

```bash
cd backend && python manage.py makemigrations bookings --name add_comunicacio_email
python manage.py migrate
```
Expected: `Applying bookings.00XX_add_comunicacio_email... OK`

- [ ] **Step 5: Run test — verify pass**

```bash
cd backend && python manage.py test bookings.tests.test_comunicacio_email -v 2
```
Expected: 3 tests pass.

- [ ] **Step 6: Update admin.py — add import, inline, and registration**

Replace the import line:
```python
from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste, Comunicacio, ComunicacioEmail
```

Add after `ComunicacioAdmin`:
```python
class ComunicacioEmailInline(admin.TabularInline):
    model = ComunicacioEmail
    extra = 0
    readonly_fields = ['tipus', 'destinatari', 'assumpte', 'enviat_a', 'enviat_per', 'exit', 'error_msg']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ComunicacioEmail)
class ComunicacioEmailAdmin(admin.ModelAdmin):
    list_display = ['tipus', 'destinatari', 'assumpte', 'reserva', 'exit', 'enviat_a']
    list_filter = ['tipus', 'exit']
    search_fields = ['destinatari', 'assumpte', 'reserva__codi_reserva']
    readonly_fields = ['reserva', 'tipus', 'destinatari', 'assumpte', 'enviat_a', 'enviat_per', 'exit', 'error_msg']
```

Add `ComunicacioEmailInline` to `ReservaAdmin.inlines`:
```python
inlines = [HosteInline, ComunicacioInline, ComunicacioEmailInline]
```

- [ ] **Step 7: Commit**

```bash
git add backend/bookings/models.py backend/bookings/migrations/ backend/bookings/admin.py backend/bookings/tests/test_comunicacio_email.py
git commit -m "feat(email): add ComunicacioEmail model, migration and admin"
```

---

### Task 3: HTML email templates (9 files)

**Files:** `backend/bookings/templates/emails/` (new directory)

- [ ] **Step 1: Create directory**

```bash
mkdir backend\bookings\templates\emails
```

- [ ] **Step 2: Create base.html** (`backend/bookings/templates/emails/base.html`)

```html
<!DOCTYPE html>
<html lang="ca">
<head>
  <meta charset="UTF-8">
  <style>
    body{margin:0;padding:20px;background:#f4f6f9;font-family:Arial,sans-serif;}
    .container{max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);}
    .header{background:#1a3a5c;padding:28px 32px;text-align:center;}
    .header h1{margin:0;color:#fff;font-size:22px;}
    .body{padding:32px;color:#333;line-height:1.6;}
    .body h2{color:#1a3a5c;margin-top:0;}
    .info-box{background:#f0f4f8;border-left:4px solid #1a3a5c;border-radius:4px;padding:16px 20px;margin:20px 0;}
    .info-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #e0e8f0;}
    .info-row:last-child{border-bottom:none;}
    .info-label{color:#666;font-size:14px;}
    .info-value{font-weight:bold;color:#1a3a5c;font-size:14px;}
    .footer{background:#f4f6f9;padding:20px 32px;text-align:center;font-size:12px;color:#888;border-top:1px solid #e0e0e0;}
    p{margin:12px 0;}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{% if immobiliaria %}{{ immobiliaria.nom_comercial }}{% else %}DomusGestor{% endif %}</h1>
    </div>
    <div class="body">{% block content %}{% endblock %}</div>
    <div class="footer">
      {% if immobiliaria %}{{ immobiliaria.nom_comercial }} &middot; {{ immobiliaria.email_contacte }} &middot; {{ immobiliaria.telefon }}{% endif %}
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 3: Create prereservada_inquili.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>Sol·licitud de reserva rebuda</h2>
<p>Hola {{ reserva.inquili.nom_complet }},</p>
<p>Hem rebut la teva sol·licitud de reserva. En breu et confirmarem la disponibilitat.</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi de reserva</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Allotjament</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  <div class="info-row"><span class="info-label">Entrada</span><span class="info-value">{{ reserva.data_entrada }}</span></div>
  <div class="info-row"><span class="info-label">Sortida</span><span class="info-value">{{ reserva.data_sortida }}</span></div>
  <div class="info-row"><span class="info-label">Persones</span><span class="info-value">{{ reserva.num_hostes }}</span></div>
</div>
<p>Gràcies per confiar en nosaltres!</p>
{% endblock %}
```

- [ ] **Step 4: Create prereservada_propietari.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>Nova sol·licitud de reserva</h2>
<p>Has rebut una nova sol·licitud de reserva per al teu immoble.</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Immoble</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  <div class="info-row"><span class="info-label">Inquilí</span><span class="info-value">{{ reserva.inquili.nom_complet }}</span></div>
  <div class="info-row"><span class="info-label">Entrada</span><span class="info-value">{{ reserva.data_entrada }}</span></div>
  <div class="info-row"><span class="info-label">Sortida</span><span class="info-value">{{ reserva.data_sortida }}</span></div>
  <div class="info-row"><span class="info-label">Persones</span><span class="info-value">{{ reserva.num_hostes }}</span></div>
</div>
<p>La reserva està pendent de confirmació.</p>
{% endblock %}
```

- [ ] **Step 5: Create confirmada_inquili.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>La teva reserva està confirmada!</h2>
<p>Hola {{ reserva.inquili.nom_complet }},</p>
<p>Ens complau confirmar la teva reserva. Et esperem!</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi de reserva</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Allotjament</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  <div class="info-row"><span class="info-label">Adreça</span><span class="info-value">{{ reserva.immoble.adreca }}</span></div>
  <div class="info-row"><span class="info-label">Entrada</span><span class="info-value">{{ reserva.data_entrada }}{% if reserva.immoble.hora_checkin_inici %} · des de les {{ reserva.immoble.hora_checkin_inici|time:"H:i" }}h{% endif %}</span></div>
  <div class="info-row"><span class="info-label">Sortida</span><span class="info-value">{{ reserva.data_sortida }}{% if reserva.immoble.hora_checkout_fi %} · fins a les {{ reserva.immoble.hora_checkout_fi|time:"H:i" }}h{% endif %}</span></div>
  <div class="info-row"><span class="info-label">Persones</span><span class="info-value">{{ reserva.num_hostes }}</span></div>
  {% if reserva.import_total %}<div class="info-row"><span class="info-label">Import total</span><span class="info-value">{{ reserva.import_total }} €</span></div>{% endif %}
</div>
{% if immobiliaria %}<p>Contacte: <strong>{{ immobiliaria.email_contacte }}</strong> · <strong>{{ immobiliaria.telefon }}</strong></p>{% endif %}
{% endblock %}
```

- [ ] **Step 6: Create confirmada_propietari.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>Reserva confirmada al teu immoble</h2>
<p>S'ha confirmat una reserva al teu immoble.</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Immoble</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  <div class="info-row"><span class="info-label">Inquilí</span><span class="info-value">{{ reserva.inquili.nom_complet }}</span></div>
  <div class="info-row"><span class="info-label">Email inquilí</span><span class="info-value">{{ reserva.inquili.email }}</span></div>
  <div class="info-row"><span class="info-label">Telèfon</span><span class="info-value">{{ reserva.inquili.telefon }}</span></div>
  <div class="info-row"><span class="info-label">Entrada</span><span class="info-value">{{ reserva.data_entrada }}</span></div>
  <div class="info-row"><span class="info-label">Sortida</span><span class="info-value">{{ reserva.data_sortida }}</span></div>
  {% if reserva.import_total %}<div class="info-row"><span class="info-label">Import</span><span class="info-value">{{ reserva.import_total }} €</span></div>{% endif %}
</div>
{% endblock %}
```

- [ ] **Step 7: Create cancelada_inquili.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>Reserva cancel·lada</h2>
<p>Hola {{ reserva.inquili.nom_complet }},</p>
<p>Et comuniquem que la teva reserva ha estat cancel·lada.</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi de reserva</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Allotjament</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  <div class="info-row"><span class="info-label">Dates</span><span class="info-value">{{ reserva.data_entrada }} – {{ reserva.data_sortida }}</span></div>
</div>
{% if immobiliaria %}<p>Contacte: <strong>{{ immobiliaria.email_contacte }}</strong></p>{% endif %}
{% endblock %}
```

- [ ] **Step 8: Create cancelada_propietari.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>Reserva cancel·lada al teu immoble</h2>
<p>S'ha cancel·lat una reserva al teu immoble.</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Immoble</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  <div class="info-row"><span class="info-label">Inquilí</span><span class="info-value">{{ reserva.inquili.nom_complet }}</span></div>
  <div class="info-row"><span class="info-label">Dates</span><span class="info-value">{{ reserva.data_entrada }} – {{ reserva.data_sortida }}</span></div>
</div>
{% endblock %}
```

- [ ] **Step 9: Create pagament_inquili.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>Pagament confirmat</h2>
<p>Hola {{ reserva.inquili.nom_complet }},</p>
<p>Hem registrat el teu pagament correctament.</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi de reserva</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Allotjament</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  {% if pagament %}
  <div class="info-row"><span class="info-label">Import pagat</span><span class="info-value">{{ pagament.import_pagament }} €</span></div>
  <div class="info-row"><span class="info-label">Data</span><span class="info-value">{{ pagament.data_pagament }}</span></div>
  <div class="info-row"><span class="info-label">Mètode</span><span class="info-value">{{ pagament.get_metode_pagament_display }}</span></div>
  {% endif %}
  <div class="info-row"><span class="info-label">Pendent</span><span class="info-value">{{ reserva.import_pendent }} €</span></div>
</div>
{% endblock %}
```

- [ ] **Step 10: Create pagament_propietari.html**

```html
{% extends "emails/base.html" %}
{% block content %}
<h2>Pagament rebut</h2>
<p>S'ha registrat un pagament en una reserva del teu immoble.</p>
<div class="info-box">
  <div class="info-row"><span class="info-label">Codi</span><span class="info-value">{{ reserva.codi_reserva }}</span></div>
  <div class="info-row"><span class="info-label">Immoble</span><span class="info-value">{{ reserva.immoble.nom_comercial }}</span></div>
  <div class="info-row"><span class="info-label">Inquilí</span><span class="info-value">{{ reserva.inquili.nom_complet }}</span></div>
  {% if pagament %}
  <div class="info-row"><span class="info-label">Import</span><span class="info-value">{{ pagament.import_pagament }} €</span></div>
  <div class="info-row"><span class="info-label">Data</span><span class="info-value">{{ pagament.data_pagament }}</span></div>
  {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 11: Commit**

```bash
git add backend/bookings/templates/
git commit -m "feat(email): add HTML email templates for all communication types"
```

---

### Task 4: emails.py — core sending functions

**Files:**
- Create: `backend/bookings/emails.py`
- Create: `backend/bookings/tests/test_emails.py`

- [ ] **Step 1: Write failing tests**

Create `backend/bookings/tests/test_emails.py`:

```python
from django.test import TestCase, override_settings
from django.core import mail
from unittest.mock import patch

from bookings.emails import enviar_prereservada, enviar_confirmada, enviar_cancelada, enviar_pagament
from bookings.models import ComunicacioEmail, ReservaBasica, Persona, PagamentReserva
from properties.models import Immoble
from users.models import InfoImmobiliaria


def _setup():
    InfoImmobiliaria.objects.create(
        nom_comercial='Gestor Test', cif='B12345678',
        adreca='Carrer 1', email_contacte='gestor@test.com', telefon='600000000',
    )
    propietari = Persona.objects.create(nom_complet='Propietari', email='propietari@test.com')
    inquili = Persona.objects.create(nom_complet='Inquilí', email='inquili@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='Carrer 1', propietari=propietari)
    reserva = ReservaBasica.objects.create(
        immoble=immoble, inquili=inquili,
        data_entrada='2026-07-01', data_sortida='2026-07-07',
        codi_reserva='RES-2026-0001', estat_reserva='prereservada',
        tipus_reserva='Direct', num_hostes=2,
        import_total='500.00', import_pendent='500.00',
    )
    return reserva


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarPrereservadaTest(TestCase):
    def test_envia_dos_emails_directa(self):
        reserva = _setup()
        enviar_prereservada(reserva)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(ComunicacioEmail.objects.filter(exit=True).count(), 2)

    def test_envia_solo_propietari_si_airbnb(self):
        reserva = _setup()
        reserva.tipus_reserva = 'Airbnb'
        enviar_prereservada(reserva)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['propietari@test.com'])

    def test_log_error_si_sense_email(self):
        reserva = _setup()
        reserva.inquili.email = ''
        reserva.inquili.save(update_fields=['email'])
        enviar_prereservada(reserva)
        log = ComunicacioEmail.objects.get(tipus='prereservada_inquili')
        self.assertFalse(log.exit)
        self.assertEqual(log.error_msg, 'Sense email')

    def test_log_error_si_smtp_falla(self):
        reserva = _setup()
        with patch('bookings.emails.send_mail', side_effect=Exception('SMTP error')):
            enviar_prereservada(reserva)
        self.assertTrue(ComunicacioEmail.objects.filter(exit=False).exists())
        self.assertIn('SMTP error', ComunicacioEmail.objects.filter(exit=False).first().error_msg)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarConfirmadaTest(TestCase):
    def test_envia_dos_emails(self):
        enviar_confirmada(_setup())
        self.assertEqual(len(mail.outbox), 2)

    def test_assumpte_conte_codi_reserva(self):
        reserva = _setup()
        enviar_confirmada(reserva)
        self.assertTrue(any('RES-2026-0001' in m.subject for m in mail.outbox))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarCanceladaTest(TestCase):
    def test_envia_dos_emails(self):
        enviar_cancelada(_setup())
        self.assertEqual(len(mail.outbox), 2)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarPagamentTest(TestCase):
    def test_envia_dos_emails(self):
        reserva = _setup()
        pagament = PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pagat',
        )
        enviar_pagament(reserva, pagament)
        self.assertEqual(len(mail.outbox), 2)
```

- [ ] **Step 2: Run — verify fail**

```bash
cd backend && python manage.py test bookings.tests.test_emails -v 2
```
Expected: ImportError — `bookings.emails` does not exist.

- [ ] **Step 3: Create backend/bookings/emails.py**

```python
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from users.models import InfoImmobiliaria
from .models import ComunicacioEmail


def _get_remitent():
    return InfoImmobiliaria.objects.first()


def _envia_i_registra(reserva, tipus, destinatari_email, assumpte, template, context, enviat_per=None):
    if not destinatari_email:
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus=tipus, destinatari='', assumpte=assumpte,
            enviat_per=enviat_per, exit=False, error_msg='Sense email',
        )
        return
    try:
        html = render_to_string(template, context)
        from_email = context['immobiliaria'].email_contacte if context.get('immobiliaria') else None
        send_mail(
            subject=assumpte, message=strip_tags(html), from_email=from_email,
            recipient_list=[destinatari_email], html_message=html, fail_silently=False,
        )
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus=tipus, destinatari=destinatari_email,
            assumpte=assumpte, enviat_per=enviat_per, exit=True,
        )
    except Exception as exc:
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus=tipus, destinatari=destinatari_email,
            assumpte=assumpte, enviat_per=enviat_per, exit=False, error_msg=str(exc),
        )


def _es_plataforma_externa(reserva):
    return reserva.tipus_reserva in ('Airbnb', 'Booking')


def _propietari_email(reserva):
    return reserva.immoble.propietari.email if reserva.immoble.propietari else ''


def enviar_prereservada(reserva):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria}
    if not _es_plataforma_externa(reserva):
        _envia_i_registra(reserva, 'prereservada_inquili', reserva.inquili.email,
                          f'Sol·licitud de reserva rebuda – {reserva.codi_reserva}',
                          'emails/prereservada_inquili.html', ctx)
    _envia_i_registra(reserva, 'prereservada_propietari', _propietari_email(reserva),
                      f'Nova sol·licitud de reserva – {reserva.immoble.nom_comercial}',
                      'emails/prereservada_propietari.html', ctx)


def enviar_confirmada(reserva):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria}
    if not _es_plataforma_externa(reserva):
        _envia_i_registra(reserva, 'confirmada_inquili', reserva.inquili.email,
                          f'La teva reserva està confirmada! – {reserva.codi_reserva}',
                          'emails/confirmada_inquili.html', ctx)
    _envia_i_registra(reserva, 'confirmada_propietari', _propietari_email(reserva),
                      f'Reserva confirmada – {reserva.immoble.nom_comercial}',
                      'emails/confirmada_propietari.html', ctx)


def enviar_cancelada(reserva):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria}
    if not _es_plataforma_externa(reserva):
        _envia_i_registra(reserva, 'cancelada_inquili', reserva.inquili.email,
                          f'Reserva cancel·lada – {reserva.codi_reserva}',
                          'emails/cancelada_inquili.html', ctx)
    _envia_i_registra(reserva, 'cancelada_propietari', _propietari_email(reserva),
                      f'Reserva cancel·lada – {reserva.immoble.nom_comercial}',
                      'emails/cancelada_propietari.html', ctx)


def enviar_pagament(reserva, pagament):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria, 'pagament': pagament}
    _envia_i_registra(reserva, 'pagament_inquili', reserva.inquili.email,
                      f'Pagament confirmat – {reserva.codi_reserva}',
                      'emails/pagament_inquili.html', ctx)
    _envia_i_registra(reserva, 'pagament_propietari', _propietari_email(reserva),
                      f'Pagament rebut – {reserva.immoble.nom_comercial}',
                      'emails/pagament_propietari.html', ctx)


def enviar_comunicacio_manual(reserva, comunicacio, usuari=None):
    immobiliaria = _get_remitent()
    from_email = immobiliaria.email_contacte if immobiliaria else None
    destinatari = comunicacio.destinatari

    if not destinatari:
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus='manual', destinatari='',
            assumpte=comunicacio.titol, enviat_per=usuari, exit=False, error_msg='Sense email',
        )
        comunicacio.estat = 'error'
        comunicacio.save(update_fields=['estat'])
        return

    try:
        send_mail(
            subject=comunicacio.titol,
            message=comunicacio.resum or '',
            from_email=from_email,
            recipient_list=[destinatari],
            html_message=f'<p>{comunicacio.resum}</p>' if comunicacio.resum else None,
            fail_silently=False,
        )
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus='manual', destinatari=destinatari,
            assumpte=comunicacio.titol, enviat_per=usuari, exit=True,
        )
        comunicacio.estat = 'enviada'
        comunicacio.save(update_fields=['estat'])
    except Exception as exc:
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus='manual', destinatari=destinatari,
            assumpte=comunicacio.titol, enviat_per=usuari, exit=False, error_msg=str(exc),
        )
        comunicacio.estat = 'error'
        comunicacio.save(update_fields=['estat'])
```

- [ ] **Step 4: Run — verify pass**

```bash
cd backend && python manage.py test bookings.tests.test_emails -v 2
```
Expected: 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/bookings/emails.py backend/bookings/tests/test_emails.py
git commit -m "feat(email): add core email sending functions with ComunicacioEmail logging"
```

---

### Task 5: Django signals

**Files:**
- Create: `backend/bookings/signals.py`
- Modify: `backend/bookings/apps.py`
- Create: `backend/bookings/tests/test_signals.py`

Note: Signal tests use `TransactionTestCase` (not `TestCase`) because signals use `transaction.on_commit`, which only fires after a real commit — `TestCase` wraps tests in a rolled-back transaction so `on_commit` never fires.

- [ ] **Step 1: Write failing tests**

Create `backend/bookings/tests/test_signals.py`:

```python
from django.test import TransactionTestCase, override_settings
from django.core import mail

from bookings.models import ComunicacioEmail, ReservaBasica, Persona, PagamentReserva
from properties.models import Immoble
from users.models import InfoImmobiliaria


def _setup():
    InfoImmobiliaria.objects.create(
        nom_comercial='Gestor', cif='B00000001',
        adreca='C/1', email_contacte='g@test.com', telefon='600000000',
    )
    propietari = Persona.objects.create(nom_complet='Propietari', email='prop@test.com')
    inquili = Persona.objects.create(nom_complet='Inquilí', email='inq@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='C/1', propietari=propietari)
    return inquili, immoble


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReservaSignalsTest(TransactionTestCase):
    def test_prereservada_envia_emails_en_crear(self):
        inquili, immoble = _setup()
        ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='prereservada', tipus_reserva='Direct',
        )
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(ComunicacioEmail.objects.count(), 2)

    def test_no_envia_si_estat_inicial_none(self):
        inquili, immoble = _setup()
        ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva=None,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_canvi_a_reservada_envia_emails(self):
        inquili, immoble = _setup()
        reserva = ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='prereservada', tipus_reserva='Direct',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        reserva.estat_reserva = 'reservada'
        reserva.save()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(ComunicacioEmail.objects.filter(tipus__contains='confirmada').count(), 2)

    def test_canvi_a_cancelada_envia_emails(self):
        inquili, immoble = _setup()
        reserva = ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='reservada', tipus_reserva='Direct',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        reserva.estat_reserva = 'cancelada'
        reserva.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_save_sense_canvi_estat_no_envia(self):
        inquili, immoble = _setup()
        reserva = ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='reservada', tipus_reserva='Direct',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        reserva.comentaris_interns = 'Canvi sense importància'
        reserva.save()
        self.assertEqual(len(mail.outbox), 0)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PagamentSignalsTest(TransactionTestCase):
    def _make_reserva(self):
        _setup()
        inquili = Persona.objects.get(nom_complet='Inquilí')
        immoble = Immoble.objects.get(nom_comercial='Pis')
        return ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='reservada', tipus_reserva='Direct',
            import_total='500.00', import_pendent='250.00',
        )

    def test_pagament_creat_com_pagat_envia_emails(self):
        reserva = self._make_reserva()
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pagat',
        )
        self.assertEqual(len(mail.outbox), 2)

    def test_pagament_pendent_no_envia(self):
        reserva = self._make_reserva()
        mail.outbox.clear()
        PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pendent',
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_canvi_pendent_a_pagat_envia_emails(self):
        reserva = self._make_reserva()
        pagament = PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pendent',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        pagament.estat = 'pagat'
        pagament.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_save_pagament_pagat_sense_canvi_no_reenvia(self):
        reserva = self._make_reserva()
        pagament = PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pagat',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        pagament.import_pagament = '251.00'
        pagament.save()
        self.assertEqual(len(mail.outbox), 0)
```

- [ ] **Step 2: Run — verify fail**

```bash
cd backend && python manage.py test bookings.tests.test_signals -v 2
```
Expected: 0 emails sent — signals not connected yet.

- [ ] **Step 3: Create backend/bookings/signals.py**

```python
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .emails import enviar_prereservada, enviar_confirmada, enviar_cancelada, enviar_pagament
from .models import ReservaBasica, PagamentReserva


@receiver(pre_save, sender=ReservaBasica)
def reserva_captura_estat_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._estat_anterior = sender.objects.get(pk=instance.pk).estat_reserva
        except sender.DoesNotExist:
            instance._estat_anterior = None
    else:
        instance._estat_anterior = None


@receiver(post_save, sender=ReservaBasica)
def reserva_post_save(sender, instance, created, **kwargs):
    estat_anterior = getattr(instance, '_estat_anterior', None)
    reserva_pk = instance.pk

    def _send():
        try:
            reserva = ReservaBasica.objects.select_related(
                'immoble', 'immoble__propietari', 'inquili'
            ).get(pk=reserva_pk)
        except ReservaBasica.DoesNotExist:
            return

        if created:
            if reserva.estat_reserva == 'prereservada':
                enviar_prereservada(reserva)
            return

        if estat_anterior == reserva.estat_reserva:
            return

        if reserva.estat_reserva == 'reservada':
            enviar_confirmada(reserva)
        elif reserva.estat_reserva == 'cancelada':
            enviar_cancelada(reserva)

    transaction.on_commit(_send)


@receiver(pre_save, sender=PagamentReserva)
def pagament_captura_estat_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._estat_anterior = sender.objects.get(pk=instance.pk).estat
        except sender.DoesNotExist:
            instance._estat_anterior = None
    else:
        instance._estat_anterior = None


@receiver(post_save, sender=PagamentReserva)
def pagament_post_save(sender, instance, created, **kwargs):
    estat_anterior = getattr(instance, '_estat_anterior', None)
    pagament_pk = instance.pk

    def _send():
        try:
            pagament = PagamentReserva.objects.select_related(
                'reserva__immoble__propietari', 'reserva__inquili'
            ).get(pk=pagament_pk)
        except PagamentReserva.DoesNotExist:
            return
        if pagament.estat == 'pagat' and estat_anterior != 'pagat':
            enviar_pagament(pagament.reserva, pagament)

    transaction.on_commit(_send)
```

- [ ] **Step 4: Connect signals in apps.py**

Replace `backend/bookings/apps.py` with:

```python
from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'

    def ready(self):
        import bookings.signals  # noqa: F401
```

- [ ] **Step 5: Run signal tests — verify pass**

```bash
cd backend && python manage.py test bookings.tests.test_signals -v 2
```
Expected: 9 tests pass.

- [ ] **Step 6: Run all bookings tests**

```bash
cd backend && python manage.py test bookings -v 2
```
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add backend/bookings/signals.py backend/bookings/apps.py backend/bookings/tests/test_signals.py
git commit -m "feat(email): add Django signals for automatic email on state changes and payments"
```

---

### Task 6: Manual send in views + email log endpoint

**Files:**
- Modify: `backend/bookings/views.py`
- Modify: `backend/bookings/serializers.py`
- Modify: `backend/bookings/urls.py`
- Create: `backend/bookings/tests/test_manual_email.py`

- [ ] **Step 1: Write failing tests**

Create `backend/bookings/tests/test_manual_email.py`:

```python
from django.test import TestCase, override_settings
from django.core import mail
from rest_framework.test import APIClient

from bookings.models import ComunicacioEmail, Comunicacio, ReservaBasica, Persona
from properties.models import Immoble
from users.models import Usuari, InfoImmobiliaria


def _setup():
    InfoImmobiliaria.objects.create(
        nom_comercial='Gestor', cif='B00000001',
        adreca='C/1', email_contacte='g@test.com', telefon='600000000',
    )
    user = Usuari.objects.create_user(nip='001', username='admin', email='a@test.com', password='pass')
    inquili = Persona.objects.create(nom_complet='Inquilí', email='inq@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='C/1')
    reserva = ReservaBasica.objects.create(
        immoble=immoble, inquili=inquili,
        data_entrada='2026-07-01', data_sortida='2026-07-07',
        estat_reserva='reservada', tipus_reserva='Direct',
        codi_reserva='RES-2026-TEST',
    )
    return user, reserva


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ManualEmailSendTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user, self.reserva = _setup()
        self.client.force_authenticate(user=self.user)

    def test_crear_comunicacio_email_envia_correu(self):
        resp = self.client.post(
            f'/bookings/reserves/{self.reserva.pk}/comunicacions/',
            {'canal': 'Email', 'titol': 'Benvinguda', 'destinatari': 'inq@test.com',
             'estat': 'pendent', 'resum': 'Benvingut!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['inq@test.com'])

    def test_crear_comunicacio_email_marca_com_enviada(self):
        self.client.post(
            f'/bookings/reserves/{self.reserva.pk}/comunicacions/',
            {'canal': 'Email', 'titol': 'Test', 'destinatari': 'inq@test.com',
             'estat': 'pendent', 'resum': 'Contingut'},
            format='json',
        )
        self.assertEqual(Comunicacio.objects.first().estat, 'enviada')

    def test_canal_no_email_no_envia(self):
        self.client.post(
            f'/bookings/reserves/{self.reserva.pk}/comunicacions/',
            {'canal': 'Telefon', 'titol': 'Trucada', 'destinatari': '600000000',
             'estat': 'enviada', 'resum': 'Fet'},
            format='json',
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_llista_emails_endpoint(self):
        ComunicacioEmail.objects.create(
            reserva=self.reserva, tipus='manual',
            destinatari='a@b.com', assumpte='Test', exit=True,
        )
        resp = self.client.get(f'/bookings/reserves/{self.reserva.pk}/emails/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['tipus'], 'manual')
```

- [ ] **Step 2: Run — verify fail**

```bash
cd backend && python manage.py test bookings.tests.test_manual_email -v 2
```
Expected: `/emails/` → 404, no emails sent.

- [ ] **Step 3: Add ComunicacioEmailSerializer to serializers.py**

Add `ComunicacioEmail` to the import line:
```python
from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste, Comunicacio, PagamentReserva, ComunicacioEmail
```

Add after `PagamentReservaSerializer`:
```python
class ComunicacioEmailSerializer(serializers.ModelSerializer):
    enviat_per_nom = serializers.CharField(source='enviat_per.username', read_only=True, default=None)

    class Meta:
        model = ComunicacioEmail
        fields = ['id', 'tipus', 'destinatari', 'assumpte', 'enviat_a', 'enviat_per', 'enviat_per_nom', 'exit', 'error_msg']
        read_only_fields = fields
```

- [ ] **Step 4: Update views.py**

Add to imports:
```python
from .emails import enviar_comunicacio_manual
from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Comunicacio, ComunicacioEmail
from .serializers import (
    PersonaSerializer, PerfilPropietariSerializer,
    ReservaSerializer, ComunicacioSerializer, ComunicacioEmailSerializer, DashboardSerializer,
)
```

Replace `ComunicacioListCreateView.perform_create`:
```python
class ComunicacioListCreateView(generics.ListCreateAPIView):
    serializer_class = ComunicacioSerializer

    def get_queryset(self):
        return Comunicacio.objects.filter(reserva_id=self.kwargs['reserva_pk'])

    def perform_create(self, serializer):
        comunicacio = serializer.save(reserva_id=self.kwargs['reserva_pk'])
        if comunicacio.canal == 'Email':
            enviar_comunicacio_manual(
                reserva=comunicacio.reserva,
                comunicacio=comunicacio,
                usuari=self.request.user,
            )
```

Add after `ComunicacioDetailView`:
```python
class ComunicacioEmailListView(generics.ListAPIView):
    serializer_class = ComunicacioEmailSerializer

    def get_queryset(self):
        return ComunicacioEmail.objects.filter(reserva_id=self.kwargs['reserva_pk'])
```

- [ ] **Step 5: Add URL to urls.py**

Add after the `comunicacio-detail` path:
```python
path(
    'reserves/<int:reserva_pk>/emails/',
    views.ComunicacioEmailListView.as_view(),
    name='comunicacio-email-list',
),
```

- [ ] **Step 6: Run — verify pass**

```bash
cd backend && python manage.py test bookings.tests.test_manual_email -v 2
```
Expected: 4 tests pass.

- [ ] **Step 7: Run all tests**

```bash
cd backend && python manage.py test bookings -v 2
```
Expected: All pass.

- [ ] **Step 8: Commit**

```bash
git add backend/bookings/views.py backend/bookings/serializers.py backend/bookings/urls.py backend/bookings/tests/test_manual_email.py
git commit -m "feat(email): wire manual email send and add email log API endpoint"
```
