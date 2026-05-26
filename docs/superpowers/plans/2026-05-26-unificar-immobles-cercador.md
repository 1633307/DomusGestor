# Unificar Immobles i Cercador — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fusionar les vistes `CercadorPage` i `InmoblesPage` en una sola vista `/inmobles` que mostra targetes enriquides (imatge, nom, carrer, localitat, hab., persones, preu) amb el panell de filtres avançats del cercador, i redirigir `/properties` a `/inmobles`.

**Architecture:** `InmoblesPage.jsx` absorbeix tota la lògica de cerca i filtres de `CercadorPage` (debounce, URLSearchParams, DatePicker). El CSS de `inmoblesPage.module.css` s'enriqueix amb els estils de miniatura, badges i panel de filtres de `cercadorPage.module.css`. Les rutes de `router.jsx` s'actualitzen per redirigir `/properties` → `/inmobles` i eliminar `CercadorPage`. Els fitxers de `CercadorPage` s'eliminen.

**Tech Stack:** React, React Router v6, Mantine DatePickerInput, react-icons (IoFilter, IoPersonAdd, IoBed), CSS Modules.

---

### Task 1: Actualitzar `inmoblesPage.module.css`

**Files:**
- Modify: `frontend/src/components/pages/inmoblesPage.module.css`

Substituir el contingut del CSS per incloure tots els estils actuals (modal, toast, badge deshabilitat) MÉS els estils de miniatura, filtres i badges de persona/hab. del cercador.

- [ ] **Step 1: Substituir el contingut de `inmoblesPage.module.css`**

Reemplaçar el contingut complet del fitxer per:

```css
.pageTitle {
  margin-bottom: 20px;
}

.pageTitleRow {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.pageTitle h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
}

.pageTitle p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 0.95rem;
}

/* Toolbar */

.propertiesToolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 0;
  flex-wrap: wrap;
  align-items: center;
}

.searchInput {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.8em 1em;
  font: inherit;
  flex: 1;
  min-width: 240px;
}

.searchInput:focus {
  outline: none;
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15);
}

.filterToggleBtn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 10px;
  padding: 0.75em 1.1em;
  font: inherit;
  font-size: 0.92rem;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  white-space: nowrap;
}

.filterToggleBtn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.loadingIndicator {
  font-size: 0.88rem;
  color: var(--muted);
  font-style: italic;
  flex-shrink: 0;
}

/* Filter panel */

.filterPanel {
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out, margin 0.3s ease-in-out;
  margin-top: 0;
  margin-bottom: 0;
}

.filterPanelOpen {
  max-height: 200px;
  opacity: 1;
  margin-top: 12px;
  margin-bottom: 22px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.filterGrid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filterItem {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filterLabel {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--muted);
}

.filterSelect {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.7em 0.9em;
  font: inherit;
  font-size: 0.92rem;
  min-width: 160px;
}

.filterSelect:focus {
  outline: none;
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15);
}

.filterNumber {
  min-width: 80px;
  max-width: 100px;
}

.datePickerInput {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font: inherit !important;
}

/* Results */

.stateMsg {
  color: var(--muted);
  margin-top: 24px;
}

.errorMsg {
  color: var(--danger);
  margin-top: 8px;
}

/* Properties grid */

.propertiesGrid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 22px;
}

.propertyCardLink {
  text-decoration: none;
  color: inherit;
}

.propertyCard {
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  cursor: pointer;
}

.propertyCard:hover {
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.12);
  transform: translateY(-2px);
}

.propertyCard h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Thumbnail */

.cardThumbnail {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid #dbeafe;
}

.cardThumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Card content */

.cardInfo {
  flex: 1;
  min-width: 0;
}

.cardSub {
  margin: 2px 0 0;
  font-size: 0.88rem;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cardCity {
  margin: 2px 0 0;
  font-size: 0.82rem;
  color: var(--muted);
  font-style: italic;
}

.cardFooter {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.priceBadge {
  display: inline-block;
  background: #dbeafe;
  color: var(--primary);
  font-size: 0.88rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.cardMeta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.metaBadge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  background: var(--surface);
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 20px;
  border: 1px solid #dbeafe;
}

/* Disabled property */

.propertyCardDisabled {
  background: #fff1f2;
  border: 1px solid #fecdd3;
}

.propertyCardDisabled:hover {
  box-shadow: 0 6px 20px rgba(225, 29, 72, 0.12);
}

.propertyCardDisabled .priceBadge {
  background: #fecdd3;
  color: #e11d48;
}

.badgeDisabled {
  display: inline-block;
  background: #fecdd3;
  color: #e11d48;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 20px;
}

/* Add button */

.addButton {
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.65em 1.3em;
  font: inherit;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s;
}

.addButton:hover {
  background: #1d4ed8;
}

/* Modal */

.modalOverlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modalBox {
  background: var(--surface);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.18);
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modalHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.modalHeader h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
}

.modalClose {
  background: transparent;
  border: none;
  color: var(--muted);
  font-size: 1rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  line-height: 1;
  transition: background 0.15s, color 0.15s;
}

.modalClose:hover {
  background: var(--border);
  color: var(--text);
}

.modalBody {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Toast */

.successToast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #16a34a;
  color: #fff;
  font-size: 0.92rem;
  font-weight: 600;
  padding: 12px 20px;
  border-radius: 10px;
  box-shadow: 0 6px 24px rgba(22, 163, 74, 0.28);
  z-index: 200;
  animation: slideIn 0.25s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Responsive */

@media (max-width: 900px) {
  .pageTitleRow {
    flex-direction: column;
    align-items: flex-start;
  }

  .propertyCard {
    flex-wrap: wrap;
  }

  .cardFooter {
    flex-direction: row;
    align-items: center;
  }

  .filterPanelOpen {
    max-height: 400px;
  }
}
```

- [ ] **Step 2: Verificar visualment que no hi ha errors de sintaxi CSS**

No hi ha comanda de verificació per CSS modules, però cal assegurar-se que el fitxer no té claus desbalancejades.

---

### Task 2: Reescriure `InmoblesPage.jsx`

**Files:**
- Modify: `frontend/src/components/pages/InmoblesPage.jsx`

Substituir el component per la versió fusionada: debounce, URLSearchParams, DatePickerInput, targetes enriquides (miniatura, ciutat, badges), badge "Deshabilitat", botó `+ Afegir Immoble` i modal.

- [ ] **Step 1: Substituir el contingut de `InmoblesPage.jsx`**

```jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { DatePickerInput } from '@mantine/dates';
import { IoFilter, IoPersonAdd, IoBed } from 'react-icons/io5';
import { api } from '../../services/api';
import PropertyForm from '../forms/propertyForm';
import styles from './inmoblesPage.module.css';

const formatDate = (date) => {
  if (!date) return null;
  const d = new Date(date);
  const month = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${d.getFullYear()}-${month}-${day}`;
};

export default function InmoblesPage() {
  const [properties, setProperties] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dates, setDates] = useState([null, null]);
  const [city, setCity] = useState('');
  const [guests, setGuests] = useState('');
  const [rooms, setRooms] = useState('');

  useEffect(() => {
    const timer = setTimeout(async () => {
      setIsLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (searchTerm) params.append('search', searchTerm);
        if (city) params.append('ciutat', city);
        if (rooms) params.append('habitacions', rooms);
        if (guests) params.append('capacitat', guests);
        if (dates[0] && dates[1]) {
          params.append('dataini', formatDate(dates[0]));
          params.append('datafi', formatDate(dates[1]));
        }
        const endpoint = `/properties/${params.toString() ? `?${params.toString()}` : ''}`;
        const data = await api.get(endpoint);
        setProperties(data.results ?? data);
      } catch (err) {
        setError(err.message || 'Error al carregar els immobles');
      } finally {
        setIsLoading(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [searchTerm, city, guests, rooms, dates, refreshKey]);

  const handleCreate = async (payload) => {
    const { propertiesApi } = await import('../../services/api');
    await propertiesApi.create(payload);
    setShowModal(false);
    setRefreshKey((k) => k + 1);
    setSuccessMsg('Immoble creat correctament!');
    setTimeout(() => setSuccessMsg(''), 3500);
  };

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Llistat Immobles</h2>
          <p>Gestiona i consulta tots els immobles registrats</p>
        </div>
        <button className={styles.addButton} onClick={() => setShowModal(true)}>
          + Afegir Immoble
        </button>
      </div>

      <div className={styles.propertiesToolbar}>
        <input
          type="text"
          placeholder="Cerca per nom o adreça..."
          className={styles.searchInput}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.currentTarget.value)}
        />
        <button
          className={styles.filterToggleBtn}
          type="button"
          onClick={() => setShowFilters(!showFilters)}
        >
          <IoFilter size={14} />
          {showFilters ? 'Tancar filtres' : 'Filtres'}
        </button>
        {isLoading && <span className={styles.loadingIndicator}>Cercant...</span>}
      </div>

      <div className={`${styles.filterPanel} ${showFilters ? styles.filterPanelOpen : ''}`}>
        <div className={styles.filterGrid}>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>Dates</label>
            <DatePickerInput
              type="range"
              placeholder="Escull un rang de dates"
              value={dates}
              onChange={setDates}
              classNames={{ input: styles.datePickerInput }}
            />
          </div>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>Localització</label>
            <select
              className={styles.filterSelect}
              value={city}
              onChange={(e) => setCity(e.target.value)}
            >
              <option value="">Totes les localitzacions</option>
              <option value="Barcelona">Barcelona</option>
              <option value="Girona">Girona</option>
              <option value="Tarragona">Tarragona</option>
              <option value="Llafranc">Llafranc</option>
              <option value="Calella">Calella</option>
              <option value="Tamariu">Tamariu</option>
            </select>
          </div>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>
              <IoPersonAdd size={14} /> Persones
            </label>
            <input
              type="number"
              className={`${styles.filterSelect} ${styles.filterNumber}`}
              value={guests}
              onChange={(e) => setGuests(e.target.value ? Number(e.target.value) : '')}
              min={1}
              placeholder="—"
            />
          </div>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>
              <IoBed size={14} /> Habitacions
            </label>
            <input
              type="number"
              className={`${styles.filterSelect} ${styles.filterNumber}`}
              value={rooms}
              onChange={(e) => setRooms(e.target.value ? Number(e.target.value) : '')}
              min={1}
              placeholder="—"
            />
          </div>
        </div>
      </div>

      {error && <p className={styles.errorMsg}>{error}</p>}

      {isLoading ? (
        <p className={styles.stateMsg}>Carregant immobles...</p>
      ) : (
        <div className={styles.propertiesGrid}>
          {properties.length === 0 && (
            <p className={styles.stateMsg}>No s'han trobat resultats.</p>
          )}
          {properties.map((property) => (
            <Link
              to={`/infoInmoble/${property.id}`}
              key={property.id}
              className={styles.propertyCardLink}
            >
              <article
                className={`${styles.propertyCard} ${property.actiu === false ? styles.propertyCardDisabled : ''}`}
              >
                <div className={styles.cardThumbnail}>
                  <img
                    src={property.fotos?.[0] || `${import.meta.env.BASE_URL}placeHolderCasa.jpg`}
                    alt={property.nom_comercial || 'Immoble'}
                  />
                </div>
                <div className={styles.cardInfo}>
                  <h3>{property.nom_comercial || 'Sense nom'}</h3>
                  <p className={styles.cardSub}>{property.adreca}</p>
                  {property.ciutat && (
                    <p className={styles.cardCity}>{property.ciutat}</p>
                  )}
                </div>
                <div className={styles.cardFooter}>
                  <span className={styles.priceBadge}>{property.preu_base_nit} €/nit</span>
                  <div className={styles.cardMeta}>
                    {property.num_habitacions > 0 && (
                      <span className={styles.metaBadge}>
                        <IoBed size={11} /> {property.num_habitacions} hab.
                      </span>
                    )}
                    {property.capacitat_maxima > 0 && (
                      <span className={styles.metaBadge}>
                        <IoPersonAdd size={11} /> {property.capacitat_maxima} pers.
                      </span>
                    )}
                    {property.actiu === false && (
                      <span className={styles.badgeDisabled}>Deshabilitat</span>
                    )}
                  </div>
                </div>
              </article>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <div className={styles.modalOverlay} onClick={() => setShowModal(false)}>
          <div className={styles.modalBox} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3>Afegir Immoble</h3>
              <button
                className={styles.modalClose}
                onClick={() => setShowModal(false)}
                aria-label="Tancar"
              >
                ✕
              </button>
            </div>
            <div className={styles.modalBody}>
              <PropertyForm
                onSubmit={handleCreate}
                onCancel={() => setShowModal(false)}
              />
            </div>
          </div>
        </div>
      )}

      {successMsg && (
        <div className={styles.successToast}>{successMsg}</div>
      )}
    </section>
  );
}
```

- [ ] **Step 2: Verificar que l'import de `propertiesApi` dins de `handleCreate` és correcte**

El `propertiesApi` s'importa de forma dinàmica dins de `handleCreate` per evitar un import circular. Si `api.js` exporta `propertiesApi` normalment, és millor afegir-lo a l'import estàtic de la primera línia:

```jsx
import { api, propertiesApi } from '../../services/api';
```

I simplificar `handleCreate`:

```jsx
const handleCreate = async (payload) => {
  await propertiesApi.create(payload);
  setShowModal(false);
  setRefreshKey((k) => k + 1);
  setSuccessMsg('Immoble creat correctament!');
  setTimeout(() => setSuccessMsg(''), 3500);
};
```

---

### Task 3: Actualitzar `router.jsx`

**Files:**
- Modify: `frontend/src/app/router.jsx`

Eliminar la ruta `/properties` que apuntava a `CercadorPage` i afegir un `<Navigate>` de `/properties` a `/inmobles`.

- [ ] **Step 1: Editar `router.jsx`**

Eliminar l'import de `CercadorPage`:
```jsx
// ELIMINAR aquesta línia:
import CercadorPage from "../components/pages/CercadorPage";
```

Substituir la ruta `/properties`:
```jsx
// CANVIAR:
<Route path="properties" element={<CercadorPage />} />

// PER:
<Route path="properties" element={<Navigate to="/inmobles" replace />} />
```

El `Navigate` ja està importat a la primera línia del fitxer (`import { Navigate, Route, Routes } from "react-router-dom";`), no cal afegir-lo.

- [ ] **Step 2: Verificar que el router compila sense errors**

```bash
cd frontend && npm run build 2>&1 | head -40
```

Expected: sense errors relacionats amb `CercadorPage`.

---

### Task 4: Eliminar fitxers de CercadorPage

**Files:**
- Delete: `frontend/src/components/pages/CercadorPage.jsx`
- Delete: `frontend/src/components/pages/cercadorPage.module.css`

- [ ] **Step 1: Eliminar els fitxers**

```bash
rm frontend/src/components/pages/CercadorPage.jsx
rm frontend/src/components/pages/cercadorPage.module.css
```

- [ ] **Step 2: Verificar que no hi ha cap altre fitxer que importi CercadorPage**

```bash
grep -r "CercadorPage\|cercadorPage" frontend/src --include="*.jsx" --include="*.js" --include="*.ts" --include="*.tsx"
```

Expected: cap resultat (o només el router.jsx que ja no l'importa).

- [ ] **Step 3: Fer build final per confirmar que tot compila**

```bash
cd frontend && npm run build 2>&1 | tail -20
```

Expected: `built in X.XXs` sense errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/pages/InmoblesPage.jsx
git add frontend/src/components/pages/inmoblesPage.module.css
git add frontend/src/app/router.jsx
git rm frontend/src/components/pages/CercadorPage.jsx
git rm frontend/src/components/pages/cercadorPage.module.css
git commit -m "feat: unify Immobles and Cercador views, redirect /properties to /inmobles"
```

---

## Self-Review

**Spec coverage:**
- [x] Targetes amb imatge, nom, carrer, localitat, hab., persones, preu → Task 2
- [x] Filtres (dates, localització, persones, habitacions) → Task 2
- [x] Búsqueda debounced → Task 2
- [x] Badge "Deshabilitat" → Task 2
- [x] Botó `+ Afegir Immoble` i modal → Task 2
- [x] CSS complet → Task 1
- [x] Redirecció `/properties` → `/inmobles` → Task 3
- [x] Eliminació de CercadorPage → Task 4

**Placeholder scan:** Cap TBD ni TODO al pla.

**Type consistency:** `propertiesApi.create`, `api.get`, `property.fotos`, `property.nom_comercial`, `property.adreca`, `property.ciutat`, `property.preu_base_nit`, `property.num_habitacions`, `property.capacitat_maxima`, `property.actiu` — tots consistents amb el codi existent de CercadorPage i InmoblesPage.
