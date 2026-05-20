# Comunicaciones por Email — DomusGestor

## Modelo de envío

Sistema **mixto**: una parte de los emails se disparan automáticamente por eventos del sistema
(cambios de estado de reserva, pagos, fechas próximas); otra parte queda disponible para que
el gestor los envíe manualmente desde la ficha de cada reserva (`reservaComunicacionsCard`).

---

## Contexto del sistema

### Estados de reserva
```
prereservada → reservada → lista → cancelada
```

| Estado | Descripción |
|--------|-------------|
| `prereservada` | Solicitud recibida, pendiente de confirmar |
| `reservada` | Reserva confirmada por el gestor |
| `lista` | Huésped presente / estancia activa |
| `cancelada` | Reserva anulada |

### Destinatarios disponibles en el modelo de datos
| Destinatario | Campo en BD |
|---|---|
| Inquilí (huésped principal) | `ReservaBasica.inquili.email` |
| Propietario del inmueble | `ReservaBasica.immoble.propietari_email` |
| Remitente (empresa gestora) | `InfoImmobiliaria.email_contacte` |

---

## A. Comunicaciones AUTOMÁTICAS

Se disparan solas cuando ocurre el evento indicado, sin intervención del gestor.

---

### A1. Pre-reserva creada
**Trigger:** Se crea una nueva reserva con estado `prereservada`
**Técnica:** Signal `post_save` en `ReservaBasica`

| Destinatario | Asunto sugerido | Contenido principal |
|---|---|---|
| Inquilí | "Solicitud de reserva recibida – [Codi reserva]" | Confirmación de recepción, fechas solicitadas, código de reserva, próximos pasos (esperar confirmación) |
| Propietari | "Nueva solicitud de reserva – [Nom comercial]" | Resumen: fechas, número de huéspedes, nombre del inquilino, código de reserva |

---

### A2. Reserva confirmada
**Trigger:** `estat_reserva` cambia de `prereservada` a `reservada`
**Técnica:** Signal `pre_save` comparando estado anterior y nuevo

| Destinatario | Asunto sugerido | Contenido principal |
|---|---|---|
| Inquilí | "¡Tu reserva está confirmada! – [Codi reserva]" | Fechas definitivas, dirección del inmueble, horarios de check-in/check-out, código de reserva, importe total, datos de contacto del gestor |
| Propietari | "Reserva confirmada – [Nom comercial] / [Dates]" | Datos del inquilino (nombre, email, teléfono), fechas, número de huéspedes, precio |

---

### A3. Pago registrado
**Trigger:** Campo `pagat` pasa a `True` o se crea un `PagamentReserva` con `estat = 'pagat'`
**Técnica:** Signal `post_save` en `ReservaBasica` o `PagamentReserva`

| Destinatario | Asunto sugerido | Contenido principal |
|---|---|---|
| Inquilí | "Pago confirmado – [Codi reserva]" | Recibo del pago: importe, fecha, concepto, saldo pendiente si lo hay |
| Propietari | "Pago recibido – [Nom comercial] / [Dates]" | Importe cobrado, reserva asociada, fecha del pago |

---

### A4. Recordatorio 7 días antes del check-in
**Trigger:** `data_entrada` = hoy + 7 días y `estat_reserva` = `reservada`
**Técnica:** Tarea periódica Celery Beat (ejecutar cada día a las 09:00)

| Destinatario | Asunto sugerido | Contenido principal |
|---|---|---|
| Inquilí | "Tu estancia se acerca – [Nom comercial]" | Recordatorio de fechas, instrucciones generales de llegada, horario de check-in, datos de contacto del gestor |
| Propietari | "Próxima llegada en 7 días – [Nom comercial]" | Resumen de la reserva, datos del inquilino |

---

### A5. Recordatorio 1 día antes del check-in
**Trigger:** `data_entrada` = mañana y `estat_reserva` = `reservada`
**Técnica:** Tarea periódica Celery Beat (ejecutar cada día a las 09:00)

| Destinatario | Asunto sugerido | Contenido principal |
|---|---|---|
| Inquilí | "Mañana es tu llegada – [Nom comercial]" | Horario exacto de llegada, código de acceso/instrucciones de entrada, WiFi, parking, teléfono de contacto de emergencia |

---

### A6. Cancelación de reserva
**Trigger:** `estat_reserva` cambia a `cancelada`
**Técnica:** Signal `pre_save` comparando estado anterior y nuevo

| Destinatario | Asunto sugerido | Contenido principal |
|---|---|---|
| Inquilí | "Reserva cancelada – [Codi reserva]" | Confirmación de cancelación, fechas de la reserva anulada, información sobre reembolsos si aplica, datos de contacto |
| Propietari | "Reserva cancelada – [Nom comercial] / [Dates]" | Detalles de la reserva cancelada, fecha de cancelación |

---

## B. Comunicaciones MANUALES

Disponibles en el componente `reservaComunicacionsCard.jsx` de la ficha de reserva.
El gestor elige cuándo enviarlas y a quién.

---

### B1. Instrucciones de check-in
**Cuándo usarla:** Cuando el gestor quiere enviar instrucciones detalladas de acceso al alojamiento.
Puede enviarse en cualquier momento una vez la reserva está confirmada.

| Destinatario | Contenido sugerido |
|---|---|
| Inquilí | Código de puerta / llave, WiFi y contraseña, parking, instrucciones específicas del inmueble, mapa o dirección exacta |

---

### B2. Bienvenida (check-in activo)
**Cuándo usarla:** Al marcar el estado como `lista`, cuando el huésped ha llegado al inmueble.

| Destinatario | Contenido sugerido |
|---|---|
| Inquilí | Bienvenida personalizada, normas de convivencia, horario de check-out, contacto del gestor para incidencias |
| Propietari | Confirmación de que el huésped ha llegado |

---

### B3. Recordatorio de pago pendiente
**Cuándo usarla:** Cuando `pagat = False` y la fecha de entrada se aproxima o ya ha pasado.

| Destinatario | Contenido sugerido |
|---|---|
| Inquilí | Importe pendiente, forma de pago aceptada, fecha límite, datos bancarios o enlace de pago |

---

### B4. Solicitud de valoración (post check-out)
**Cuándo usarla:** Unos días después de que el huésped se haya marchado.

| Destinatario | Contenido sugerido |
|---|---|
| Inquilí | Agradecimiento por la estancia, invitación a dejar una reseña, enlace o contacto para feedback |

---

### B5. Comunicación libre
**Cuándo usarla:** Cualquier comunicación específica que el gestor necesite enviar fuera de las plantillas predefinidas.

| Destinatario | Contenido |
|---|---|
| Inquilí y/o Propietari | Asunto libre + cuerpo de texto libre |

---

## C. Resumen global por destinatario

### Inquilí
| Evento | Tipo | Prioridad |
|--------|------|-----------|
| Pre-reserva creada | Automático | Alta |
| Reserva confirmada | Automático | Alta |
| Pago confirmado | Automático | Alta |
| Recordatorio 7 días antes | Automático | Media |
| Recordatorio 1 día antes | Automático | Alta |
| Cancelación | Automático | Alta |
| Instrucciones check-in | Manual | Alta |
| Bienvenida | Manual | Media |
| Recordatorio pago pendiente | Manual | Media |
| Solicitud valoración | Manual | Baja |
| Comunicación libre | Manual | Variable |

### Propietari
| Evento | Tipo | Prioridad |
|--------|------|-----------|
| Nueva pre-reserva | Automático | Alta |
| Reserva confirmada | Automático | Alta |
| Pago recibido | Automático | Alta |
| Recordatorio 7 días antes | Automático | Media |
| Cancelación | Automático | Alta |
| Bienvenida/llegada del huésped | Manual | Baja |
| Comunicación libre | Manual | Variable |

---

## D. Consideraciones técnicas para la implementación

### Infraestructura necesaria

| Componente | Propósito |
|---|---|
| **Django signals** (`post_save`, `pre_save`) | Detectar cambios de estado en `ReservaBasica` y `PagamentReserva` |
| **Celery + Celery Beat** | Tareas programadas para recordatorios temporales (A4, A5) |
| **Redis** | Broker de mensajes para Celery |
| **Django EmailBackend** (SMTP) | Envío real de emails vía SendGrid, Mailgun u SMTP propio |
| **Plantillas HTML** | Templates Django por tipo de email (texto + HTML) |

### Datos necesarios (todos disponibles en el modelo actual)

```python
reserva.codi_reserva                        # Código único de reserva
reserva.inquili.email                       # Email del huésped
reserva.inquili.nom_complet                 # Nombre del huésped
reserva.immoble.nom_comercial               # Nombre del inmueble
reserva.immoble.propietari_email            # Email del propietario
reserva.immoble.hora_checkin_inici / fi     # Horario check-in
reserva.immoble.hora_checkout_inici / fi    # Horario check-out
reserva.data_entrada / data_sortida         # Fechas de la estancia
reserva.num_hostes                          # Número de huéspedes
InfoImmobiliaria.email_contacte             # Remitente (empresa gestora)
InfoImmobiliaria.nom_comercial              # Nombre empresa en firma
```

### Modelo de registro de comunicaciones enviadas

Para mostrar el historial en `reservaComunicacionsCard.jsx` y evitar duplicados en los automáticos,
se recomienda crear un modelo `ComunicacioEmail` en `bookings/models.py`:

```
ComunicacioEmail
  - reserva (FK ReservaBasica)
  - tipus (prereservada_inquili, confirmada_inquili, pagament_inquili, ...)
  - destinatari_email
  - assumpte
  - enviat_a (DateTimeField, auto_now_add)
  - enviat_per (null = automàtic, FK Usuari = manual)
  - exit (BooleanField, True si SMTP no devolvió error)
```

---

## E. Casos especiales

- **Reservas de Airbnb/Booking (tipus_reserva != 'directa'):** Valorar si los automáticos al
  inquilino deben desactivarse para evitar duplicar comunicaciones que ya gestiona la plataforma
  externa. Los del propietario sí deberían enviarse siempre.

- **Cambio de fechas:** Si se modifica `data_entrada` o `data_sortida` en una reserva ya
  `reservada`, enviar un email de "Cambio de fechas" al inquilino y al propietario.

- **Reactivación de reserva cancelada:** Si `estat_reserva` vuelve de `cancelada` a `reservada`,
  tratar como una nueva confirmación y enviar los emails correspondientes.
