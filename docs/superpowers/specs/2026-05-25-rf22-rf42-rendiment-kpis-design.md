# RF-22 / RF-42: Informes de rendiment i KPIs — Design Spec

**Data:** 2026-05-25  
**Requeriments:** RF-22 (Informes de rendiment per propietaris), RF-42 (Estadístiques i KPIs de rendiment)

---

## 1. Abast

Dues àrees de la mateixa entrega:

1. **Dashboard global (RF-42):** Ampliar el dashboard amb nous KPIs i dos gràfics de barres.
2. **Informe de rendiment per propietari (RF-22):** Afegir una secció "Informes de rendiment" dins `InfoPersonaPage`, accessible des del `Sidebar`, visible únicament per a persones amb `perfil_propietari`.

---

## 2. Backend

### 2.1 Extensió de `DashboardView`

`GET /api/bookings/dashboard/` retorna els camps existents més:

| Camp | Tipus | Descripció |
|---|---|---|
| `ingressos_totals` | `string` (decimal) | Suma de `import_pagat` de totes les reserves |
| `reserves_proximes_7_dies` | `int` | Reserves amb `data_entrada` entre avui i +7 dies |
| `reserves_per_estat` | `object` | `{prereservada, reservada, lista, cancelada}` → count |
| `ingressos_per_mes` | `array` | `[{mes: "YYYY-MM", ingressos: "0.00"}, ...]` — últims 6 mesos |

**Implementació:** Tot dins `DashboardView.get()` usant `aggregate(Sum(...))`, `filter(data_entrada__range=...)` i `annotate` agrupat per mes via `TruncMonth`.

`DashboardSerializer` s'amplia per incloure els nous camps.

### 2.2 Nou endpoint: Rendiment propietari

`GET /api/bookings/persones/{id}/rendiment/`

**Vista:** `RendimentPropietariView(APIView)` a `bookings/views.py`.

**Resposta:**
```json
{
  "num_immobles": 3,
  "immobles_actius": 2,
  "total_reserves": 18,
  "ingressos_totals": "8450.00",
  "reserves_per_immoble": [
    {
      "id": 1,
      "nom": "Apt Gràcia",
      "num_reserves": 10,
      "ingressos": "4200.00",
      "actiu": true
    }
  ]
}
```

**Lògica:**
- Filtra `Immoble.objects.filter(propietari_id=id)`.
- Per cada immoble: `reserves__count` i `reserves__import_pagat__sum` via `annotate`.
- Retorna 404 si la persona no existeix, 400 si no té `perfil_propietari`.

**URL:** afegir a `bookings/urls.py`:
```python
path('persones/<int:pk>/rendiment/', views.RendimentPropietariView.as_view())
```

**API client:** afegir a `personesApi` a `api.js`:
```js
rendiment: (id) => api.get(`/bookings/persones/${id}/rendiment/`)
```

---

## 3. Frontend — Dashboard

### 3.1 Nous KPI cards

S'afegeixen 2 cards al `dashboardGrid` existent:

- **Ingressos totals** → `stats.ingressos_totals` formatat com `X.XXX €`; subtítol "Total cobrat"
- **Properes entrades** → `stats.reserves_proximes_7_dies`; subtítol "pròxims 7 dies"

### 3.2 Secció de gràfics

Sota el grid de KPIs, un nou `chartsRow` (CSS grid 2 columnes, apilat en mòbil).

**Gràfic 1 — Reserves per estat** (`BarChart` de Recharts)
- Eix X: `prereservada`, `reservada`, `lista`, `cancelada`
- Eix Y: nombre de reserves
- Tooltip amb el count exacte

**Gràfic 2 — Ingressos mensuals** (`BarChart` de Recharts)
- Dades: `stats.ingressos_per_mes` (últims 6 mesos)
- Eix X: mes abreujat (gen, feb, mar...)
- Eix Y: euros
- Tooltip amb import formatat

### 3.3 CSS (`DashboardPage.module.css`)

Afegir:
- `.chartsRow`: grid 2 cols, gap 18px, `@media` a 1 col sota 768px
- `.chartCard`: mateixa aparença que `.dashboardCard` (fons `#eff6ff`, border `#dbeafe`, radius 12px)
- `.chartTitle`: h3 dins chartCard
- `.metric`: mida gran per als valors KPI (ja existent al JSX però absent al CSS — afegir)

---

## 4. Frontend — InfoPersonaPage

### 4.1 Layout

`InfoPersonaPage` adopta el patró `templateGrid` + `Sidebar`:

- Importar `Sidebar` de `../layout/Sidebar`
- Substituir el div `.page` per la mateixa estructura que `InfoInmoblePage`:
  ```jsx
  <section>
    <div className={styles.templateGrid}>
      <Sidebar seccions={seccions} ... />
      <div className={styles.perfilCard}>
        {/* contingut per secció */}
      </div>
    </div>
  </section>
  ```

**Seccions del Sidebar** (calculades amb `useMemo` quan carreguen les dades):
- Sempre: `{ id: "perfil", label: "Perfil" }`
- Si `persona.perfil_propietari !== null`: `{ id: "rendiment", label: "Informes de rendiment" }`

El `FooterActions` es mou dins del bloc `seccioActiva === "perfil"`.

### 4.2 Nou component: `RendimentPropietariCard`

**Fitxer:** `frontend/src/Cards/RendimentPropietariCard.jsx`

**Props:** `{ personaId }`

**Comportament:**
1. `useEffect` → crida `personesApi.rendiment(personaId)` en muntar
2. Mostra estat de càrrega / error
3. Renderitza:
   - **4 KPI chips** en grid: immobles totals, immobles actius, total reserves, ingressos totals
   - **BarChart** (Recharts, ResponsiveContainer): ingressos per immoble
   - **Llista d'immobles**: cada fila → nom (link a `/inmobles/{id}`), badge actiu/inactiu, nº reserves, ingressos

**CSS:** `RendimentPropietariCard.module.css` amb `.kpiGrid`, `.kpiChip`, `.kpiValue`, `.kpiLabel`, `.immobleRow`.

### 4.3 Ús a InfoPersonaPage

```jsx
{seccioActiva === "rendiment" && persona.perfilPropietariId && (
  <RendimentPropietariCard personaId={id} />
)}
```

---

## 5. Fitxers afectats

| Fitxer | Canvi |
|---|---|
| `backend/bookings/views.py` | Estendre `DashboardView`; afegir `RendimentPropietariView` |
| `backend/bookings/serializers.py` | Estendre `DashboardSerializer` |
| `backend/bookings/urls.py` | Afegir URL rendiment propietari |
| `frontend/src/services/api.js` | Afegir `personesApi.rendiment` |
| `frontend/src/components/pages/DashboardPage.jsx` | Nous KPIs + gràfics |
| `frontend/src/components/pages/DashboardPage.module.css` | `.chartsRow`, `.chartCard`, `.metric` |
| `frontend/src/components/pages/InfoPersonaPage.jsx` | Layout Sidebar + secció rendiment |
| `frontend/src/components/pages/InfoPersonaPage.module.css` | `.templateGrid`, `.perfilCard` |
| `frontend/src/Cards/RendimentPropietariCard.jsx` | Nou component |
| `frontend/src/Cards/RendimentPropietariCard.module.css` | Nous estils |

---

## 6. Fora d'abast

- Filtres per rang de dates (possible extensió futura — Enfocament B)
- Export PDF/Excel de l'informe
- Notificacions o alertes basades en KPIs
