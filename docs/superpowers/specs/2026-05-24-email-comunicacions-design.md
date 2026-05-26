# Sistema d'enviament de correus electrònics — DomusGestor

**Data:** 2026-05-24
**Estat:** Aprovat per implementar

## Resum

Sistema mixt d'enviament de correus: automàtics via Django signals (canvis d'estat de reserva i pagaments) i manuals via API des de la fitxa de reserva. Transport: Gmail SMTP natiu de Django (sense paquets addicionals). Sense Celery (recordatoris temporals descartats).

## Arquitectura

```
Canvi d'estat / pagament
        │
        ▼
  Django Signal ──► emails.py ──► Gmail SMTP ──► ComunicacioEmail (log)

Comunicació manual (UI card)
        │
        ▼
  API POST /comunicacions/ ──► emails.py ──► Gmail SMTP ──► ComunicacioEmail (log)
```

## Model nou: `ComunicacioEmail`

Log immutable de tots els enviaments SMTP. Separat del model `Comunicacio` (log manual multi-canal).

```python
class ComunicacioEmail(models.Model):
    TIPUS_CHOICES = [
        ('prereservada_inquili', ...),
        ('prereservada_propietari', ...),
        ('confirmada_inquili', ...),
        ('confirmada_propietari', ...),
        ('cancelada_inquili', ...),
        ('cancelada_propietari', ...),
        ('pagament_inquili', ...),
        ('pagament_propietari', ...),
        ('manual', ...),
    ]
    reserva       = FK(ReservaBasica, CASCADE)
    tipus         = CharField(choices=TIPUS_CHOICES)
    destinatari   = EmailField()
    assumpte      = CharField(200)
    enviat_a      = DateTimeField(auto_now_add=True)
    enviat_per    = FK(Usuari, null=True)   # null = automàtic via signal
    exit          = BooleanField()
    error_msg     = TextField(blank=True)
```

## Triggers automàtics (signals)

| Event | Signal | Destinataris | Condicions especials |
|-------|--------|--------------|----------------------|
| Reserva nova amb `prereservada` | `post_save` (created=True) | Inquilí + Propietari | — |
| `estat_reserva` → `reservada` | `pre_save` (canvi detectat) | Inquilí + Propietari | Ometre inquilí si `tipus_reserva != 'Direct'` |
| `estat_reserva` → `cancelada` | `pre_save` (canvi detectat) | Inquilí + Propietari | Ometre inquilí si `tipus_reserva != 'Direct'` |
| `PagamentReserva.estat` → `pagat` | `post_save` | Inquilí + Propietari | — |

**Obtenció d'emails:**
- Inquilí: `reserva.inquili.email`
- Propietari: `reserva.immoble.propietari.email` (via FK `Immoble.propietari → Persona`)
- Remitent: `InfoImmobiliaria.email_contacte` (primer registre)

Si un email és buit, s'omet sense error.

## Enviament manual

`ComunicacioListCreateView.perform_create`: si `canal == 'Email'`, crida `enviar_comunicacio_manual()`. Actualitza `Comunicacio.estat` a `'enviada'` o `'error'` segons el resultat SMTP.

Re-enviament: el gestor crea una nova `Comunicacio` amb les mateixes dades.

## Fitxers nous

| Fitxer | Contingut |
|--------|-----------|
| `bookings/signals.py` | Signals `post_save`/`pre_save` per `ReservaBasica` i `PagamentReserva` |
| `bookings/emails.py` | Funcions `enviar_*` per cada tipus + helper `_log_enviament` |
| `bookings/templates/emails/base.html` | Layout HTML base |
| `bookings/templates/emails/prereservada_inquili.html` | Template per cada tipus (×8) |
| `bookings/apps.py` | Connecta signals al `ready()` |

## Fitxers modificats

| Fitxer | Canvi |
|--------|-------|
| `bookings/models.py` | Afegir `ComunicacioEmail` |
| `bookings/serializers.py` | Afegir `ComunicacioEmailSerializer` |
| `bookings/views.py` | `perform_create` a `ComunicacioListCreateView` per enviar manual |
| `bookings/urls.py` | Afegir endpoint `GET /reserves/{id}/emails/` |
| `bookings/admin.py` | Registrar `ComunicacioEmail` |
| `domusgestor/settings.py` | Variables EMAIL_* llegides de `.env` |
| `backend/.env` | Credencials Gmail SMTP |

## Configuració Gmail SMTP

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=compte@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx   # App Password 16 caràcters
DEFAULT_FROM_EMAIL=DomusGestor <compte@gmail.com>
```

## Casos especials

- **Airbnb/Booking:** `tipus_reserva != 'Direct'` → ometre automàtics a l'inquilí (la plataforma externa ja notifica). Sí enviar al propietari.
- **Email buit:** Si inquilí o propietari no té email, log amb `exit=False, error_msg='Sense email'`.
- **Error SMTP:** Capturar excepció, log amb `exit=False, error_msg=str(exc)`. No llançar excepció al signal (no ha de trencar el flux de la reserva).
