# Disseny: Reestructuració Backend de Persones

**Data:** 2026-05-20
**Estat:** Aprovat

---

## Context

L'aplicació actual té les dades de persones disperses en tres llocs:
- `InquiliBasic` (app `bookings`) — dades personals + facturació d'inquilins
- Camps `propietari_*` incrustats a `Immoble` (app `properties`) — sense model separat
- `Hoste` (app `bookings`) — camps personals propis, sense vincle a cap persona registrada

L'objectiu és unificar-ho en una taula `Persona` base amb sub-perfils opcionals per a inquilins i propietaris.

---

## Nous Models (app `bookings`)

### `Persona`
Taula base comuna per a totes les persones (inquilins i propietaris).

| Camp | Tipus | Notes |
|------|-------|-------|
| `nom_complet` | CharField(150) | |
| `genere` | CharField(10) | choices: Home, Dona, Altres |
| `tipus_document` | CharField(15) | choices: DNI, NIE, Passaport |
| `dni_passaport` | EncryptedTextField | xifrat |
| `dni_passaport_hash` | CharField(64) | HMAC per unicitat, null=True |
| `nacionalitat` | CharField(80) | |
| `data_naixement` | DateField | null=True |
| `residencia` | TextField | |
| `email` | EmailField | |
| `telefon` | CharField(30) | |

### `PerfilInquili`
Marca que una persona és inquilí. Sense camps addicionals ara.

| Camp | Tipus | Notes |
|------|-------|-------|
| `persona` | OneToOneField(Persona) | related_name='perfil_inquili' |

### `PerfilPropietari`
Dades fiscals i de facturació, exclusives de propietaris.

| Camp | Tipus | Notes |
|------|-------|-------|
| `persona` | OneToOneField(Persona) | related_name='perfil_propietari' |
| `nom_fiscal` | CharField(150) | |
| `nif_cif` | CharField(30) | |
| `adreca_facturacio` | TextField | adreça fiscal/facturació |
| `codi_postal_facturacio` | CharField(12) | |
| `ciutat_facturacio` | CharField(100) | |
| `provincia_facturacio` | CharField(100) | |
| `pais_facturacio` | CharField(100) | |
| `email_facturacio` | EmailField | |
| `telefon_facturacio` | CharField(30) | |
| `iban` | CharField(34) | migrat des de Immoble.propietari_iban |
| `observacions_facturacio` | TextField | |
| `dades_facturacio` | EncryptedTextField | llegat xifrat |

---

## Canvis a Models Existents

### `ReservaBasica`
- `inquili`: canvia de `ForeignKey(InquiliBasic)` → `ForeignKey(Persona, on_delete=PROTECT, related_name='reserves')`

### `Hoste`
- Afegir: `persona = ForeignKey(Persona, null=True, blank=True, on_delete=SET_NULL, related_name='hostes')`
- Es manté la resta de camps existents (per hostes anònims sense Persona registrada)

### `Immoble`
- Afegir: `propietari = ForeignKey(Persona, null=True, blank=True, on_delete=SET_NULL, related_name='immobles')`
- Eliminar: `propietari_nom`, `propietari_dni`, `propietari_email`, `propietari_telefon`, `propietari_adreca`, `propietari_iban`

### `InquiliBasic`
- **Eliminat completament** després de la migració de dades.

---

## Estratègia de Migració (3 migracions seqüencials)

### Migració 1 — Esquema nou
- Crear `Persona`, `PerfilInquili`, `PerfilPropietari`
- Afegir `Hoste.persona` (FK nullable)
- Afegir `ReservaBasica.inquili_nou` (FK nullable a `Persona`, temporal)
- Afegir `Immoble.propietari` (FK nullable)

### Migració 2 — Dades
Per cada `InquiliBasic`:
1. Crear `Persona` amb els camps personals
2. Crear `PerfilInquili` vinculat
3. Si té dades fiscals (nom_fiscal o nif_cif no buits) → crear `PerfilPropietari`
4. Actualitzar `ReservaBasica.inquili_nou` apuntant a la nova `Persona`

Per cada `Immoble` amb `propietari_nom` no buit:
1. Buscar `Persona` existent per `propietari_email` o `propietari_dni` (deduplicació)
2. Si no existeix → crear nova `Persona` + `PerfilPropietari` amb `iban` i dades fiscals
3. Assignar `Immoble.propietari` FK

### Migració 3 — Neteja
- Eliminar `ReservaBasica.inquili` (l'antic FK a `InquiliBasic`)
- Renombrar `ReservaBasica.inquili_nou` → `inquili`
- Eliminar model `InquiliBasic`
- Eliminar camps `propietari_*` d'`Immoble`

---

## API

### Nous endpoints
```
GET    /api/bookings/persones/           — llistar totes les persones
POST   /api/bookings/persones/           — crear nova persona
GET    /api/bookings/persones/{id}/      — detall d'una persona
PUT    /api/bookings/persones/{id}/      — actualitzar persona completa
PATCH  /api/bookings/persones/{id}/      — actualitzar parcialment
DELETE /api/bookings/persones/{id}/      — eliminar persona
```

### Eliminats
```
/api/bookings/inquilins/        — eliminat
/api/bookings/inquilins/{id}/   — eliminat
```

### `PersonaSerializer`
Exposa:
- Camps de `Persona`
- `perfil_inquili` (nested, null si no existeix)
- `perfil_propietari` (nested amb dades fiscals, null si no existeix)
- `reserves` (llista resumida de reserves vinculades, read-only)

### Actualitzacions
- `ReservaSerializer`: camp `inquili` ara referencia `Persona`
- `ImmobleSerializer`: camp `propietari` ara és FK a `Persona` (substitueix `propietari_*` fields)
- `HosteSerializer`: afegir camp `persona` (FK optional, read/write)

---

## Fitxers afectats

**Backend:**
- `backend/bookings/models.py` — nous models + canvis a existents
- `backend/bookings/serializers.py` — nous serialitzadors + actualitzacions
- `backend/bookings/views.py` — noves vistes PersonaListCreateView, PersonaDetailView
- `backend/bookings/urls.py` — nous URLs, eliminar inquilins
- `backend/bookings/migrations/` — 3 migracions noves
- `backend/properties/models.py` — afegir propietari FK, eliminar propietari_* fields
- `backend/properties/serializers.py` — actualitzar ImmobleSerializer

**Frontend (pendent, sub-projecte 2):**
- `frontend/src/services/api.js` — canviar inquilinsApi per personesApi
- `frontend/src/components/pages/PersonesPage.jsx`
- `frontend/src/components/pages/InfoPersonaPage.jsx`
- `frontend/src/components/pages/InfoInmoblePage.jsx`

---

## Decisions de disseny

- **Deduplicació a migració:** Si un `InquiliBasic` i un `Immoble.propietari_*` comparteixen email o DNI, es crea una sola `Persona` i se li assignen tant `PerfilInquili` com `PerfilPropietari`.
- **Hostes anònims:** `Hoste.persona` és nullable. Si l'hoste no és una persona registrada, es deixa null i els camps del `Hoste` actuen com a registre autònom.
- **Xifrat:** `Persona.dni_passaport` hereta el mecanisme `EncryptedTextField` + hash HMAC de `InquiliBasic`.
- **Backwards compat:** No es mantenen els endpoints `/inquilins/` — el frontend s'actualitzarà en el sub-projecte 2.
