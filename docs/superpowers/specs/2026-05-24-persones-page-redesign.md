# Spec: Persones Page — Fix document, filtres i redisseny visual

**Data:** 2026-05-24  
**Estat:** Aprovat

---

## Resum

Tres millores sobre la finestra de persones:
1. Corregir el camp document que mostra el valor HMAC en lloc del text pla.
2. Afegir filtre de rol (Tots / Hostes / Propietaris) a la llista.
3. Redissenyar el frontend perquè segueixi la mateixa línia visual que Immobles i Reserves.

---

## 1. Fix: Document hasheado

### Diagnòstic
El camp `Persona.dni_passaport` és un `TextField` pla. El camp `Persona.dni_passaport_hash` és el HMAC-SHA256 i NO s'exposa al serialitzador. Malgrat això, alguns registres a la BD poden tenir el valor hash (64 caràcters hex) emmagatzemat a `dni_passaport` en lloc del document real, fruit d'un bug en migracions antigues o en scripts de creació de dades.

### Fix
- Afegir una migració de dades (`RunPython`) que detecti i elimini els valors corruptes: qualsevol registre on `len(dni_passaport) == 64` i tots els caràcters són hex `[0-9a-f]` → buidar `dni_passaport` a `''`, perquè cap número de document real té 64 caràcters hexadecimals (és el format exacte d'un HMAC-SHA256).
- No es pot recuperar el text original del document si només s'ha guardat el hash — la neteja és la única opció segura.

### Canvis backend
- `backend/bookings/migrations/0014_fix_dni_passaport_hash_en_plain.py`: migració de neteja.
- `backend/bookings/views.py` → `PersonaListCreateView`: afegir `select_related('perfil_inquili', 'perfil_propietari')` per eliminar N+1 queries.

---

## 2. Filtre Tots / Hostes / Propietaris

### Lògica
El serialitzador ja retorna `perfil_inquili` i `perfil_propietari` per a cada persona. El filtre és **client-side**: es filtra l'array local per presència d'aquests camps.

- `Tots`: sense filtre.
- `Hostes`: `persona.perfil_inquili !== null`.
- `Propietaris`: `persona.perfil_propietari !== null`.

Una persona pot tenir els dos perfils simultàniament (apareix a "Hostes" i a "Propietaris" però no a "Tots" doble — simplement és visible en ambdós filtres).

### Canvis frontend
- `PersonesPage.jsx`: estat `roleFilter` ('all' | 'inquili' | 'propietari'). `useMemo` per filtrar i ordenar.
- Pills de filtre: tres botons tipus toggle, disseny igual que els pills d'estat (sense implementar al projecte ara, s'aplica el patró de reserves adaptant-lo a pills de selecció).

---

## 3. Redisseny visual de PersonesPage

### Patró existent (Immobles / Reserves)
- Títol + subtítol + botó d'acció a la dreta.
- Toolbar: input de cerca + controls addicionals.
- Grid de cards: `flex-direction: column`, `gap: 12px`.
- Card: `background: #eff6ff`, `border: 1px solid #dbeafe`, `border-radius: 12px`, `padding: 16px 20px`, hover `translateY(-2px)` + `box-shadow: 0 6px 20px rgba(37, 99, 235, 0.12)`.
- Footer de card: badges arrodonits.

### Cards de persona
```
┌────────────────────────────────────────┬──────────────────┐
│ [Nom Cognom]  ·  Document · Email      │  [Hoste]         │
│ Telèfon · Nacionalitat                 │  [Propietari]    │
└────────────────────────────────────────┴──────────────────┘
```

- **Esquerra (`cardInfo`)**: nom en negreta, seguit de document (o email si buit), telèfon, nacionalitat en gris.
- **Dreta (`cardFooter`)**: badges de rol — `Hoste` (fons `#dbeafe`, text `#1d4ed8`) i `Propietari` (fons `#dcfce7`, text `#15803d`).
- El link cobreix tota la card (igual que propertyCardLink a immobles).

### Toolbar
```
[Cercar per nom, document o email...] [Tots] [Hostes] [Propietaris]
```
- Pills: fons `var(--surface)`, border `var(--border)`. Actiu: fons `#2563eb`, text blanc.

### Canvis frontend
- `PersonesPage.jsx`: reescriure component.
- `PersonesPage.module.css`: reescriure CSS seguint exactament el patró d'immobles.

---

## Fitxers afectats

| Fitxer | Canvi |
|--------|-------|
| `backend/bookings/migrations/0014_fix_dni_passaport_hash_en_plain.py` | Nova migració de neteja de dades |
| `backend/bookings/views.py` | `select_related` a `PersonaListCreateView` |
| `frontend/src/components/pages/PersonesPage.jsx` | Reescriptura completa |
| `frontend/src/components/pages/PersonesPage.module.css` | Reescriptura completa |

---

## Fora d'abast

- No es modifica `InfoPersonaPage.jsx` ni `PersonaFormSection.jsx`.
- No es canvia el serialitzador ni els endpoints.
- No es fa filtre backend (query params) — client-side és suficient.
