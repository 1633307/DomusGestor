# RF-22 / RF-42: Informes de rendiment i KPIs — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Afegir KPIs i gràfics al dashboard global, i un informe de rendiment per propietari dins InfoPersonaPage (sidebar "Informes de rendiment").

**Architecture:** Backend estén `DashboardView` amb nous agregats i afegeix `RendimentPropietariView`. Frontend actualitza `DashboardPage` amb Recharts i reestructura `InfoPersonaPage` seguint el patró Sidebar+templateGrid d'`InfoInmoblePage`, amb un nou component `RendimentPropietariCard`.

**Tech Stack:** Django REST Framework, React 19, Recharts, CSS Modules

---

## File Map

| Fitxer | Canvi |
|---|---|
| `backend/bookings/serializers.py` | Estendre `DashboardSerializer` amb 4 camps nous |
| `backend/bookings/views.py` | Estendre `DashboardView`; afegir `RendimentPropietariView` |
| `backend/bookings/urls.py` | Afegir ruta rendiment propietari |
| `frontend/src/services/api.js` | Afegir `personesApi.rendiment` |
| `frontend/src/components/pages/DashboardPage.jsx` | 2 KPI cards nous + 2 gràfics Recharts |
| `frontend/src/components/pages/DashboardPage.module.css` | `.metric`, `.chartsRow`, `.chartCard`, `.chartTitle` |
| `frontend/src/Cards/RendimentPropietariCard.jsx` | Nou component (KPIs + gràfic + llista immobles) |
| `frontend/src/Cards/RendimentPropietariCard.module.css` | Estils del component |
| `frontend/src/components/pages/InfoPersonaPage.jsx` | Layout Sidebar+templateGrid; secció rendiment |
| `frontend/src/components/pages/InfoPersonaPage.module.css` | Afegir `.templateGrid`, `.perfilCard` |

---

## Task 1: Estendre DashboardSerializer

**Files:**
- Modify: `backend/bookings/serializers.py` (línia 296–301)

- [ ] **Step 1: Substituir `DashboardSerializer` amb la versió ampliada**

Substituir el bloc existent (línies 296–301):

```python
class DashboardSerializer(serializers.Serializer):
    total_reserves = serializers.IntegerField()
    total_immobles = serializers.IntegerField()
    total_inquilins = serializers.IntegerField()
    immobles_actius = serializers.IntegerField()
    reserves_pagades = serializers.IntegerField()
    ingressos_totals = serializers.DecimalField(max_digits=12, decimal_places=2)
    reserves_proximes_7_dies = serializers.IntegerField()
    reserves_per_estat = serializers.DictField(child=serializers.IntegerField())
    ingressos_per_mes = serializers.ListField(child=serializers.DictField())
```

- [ ] **Step 2: Commit**

```bash
git add backend/bookings/serializers.py
git commit -m "feat(dashboard): extend DashboardSerializer with revenue and chart fields"
```

---

## Task 2: Estendre DashboardView

**Files:**
- Modify: `backend/bookings/views.py`

- [ ] **Step 1: Afegir imports al principi de `views.py`**

Afegir just sota la línia `from rest_framework.views import APIView`:

```python
from datetime import date, timedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth
```

- [ ] **Step 2: Substituir el mètode `DashboardView.get`**

Substituir tot el cos de la classe `DashboardView`:

```python
class DashboardView(APIView):
    def get(self, request):
        avui = date.today()

        # Últims 6 mesos: calcular el primer dia d'inici
        m = avui.month - 5
        y = avui.year
        while m <= 0:
            m += 12
            y -= 1
        inici_6_mesos = date(y, m, 1)

        mensuals_qs = (
            ReservaBasica.objects
            .filter(data_entrada__gte=inici_6_mesos)
            .annotate(mes_trunc=TruncMonth('data_entrada'))
            .values('mes_trunc')
            .annotate(ingressos=Sum('import_pagat'))
            .order_by('mes_trunc')
        )
        ingressos_dict = {
            row['mes_trunc'].strftime('%Y-%m'): float(row['ingressos'] or 0)
            for row in mensuals_qs
        }
        ingressos_per_mes = []
        for i in range(5, -1, -1):
            mi = avui.month - i
            yi = avui.year
            while mi <= 0:
                mi += 12
                yi -= 1
            key = f"{yi:04d}-{mi:02d}"
            ingressos_per_mes.append({'mes': key, 'ingressos': ingressos_dict.get(key, 0)})

        estats = ['prereservada', 'reservada', 'lista', 'cancelada']
        reserves_per_estat = {
            estat: ReservaBasica.objects.filter(estat_reserva=estat).count()
            for estat in estats
        }

        data = {
            'total_reserves': ReservaBasica.objects.count(),
            'total_immobles': Immoble.objects.count(),
            'total_inquilins': PerfilInquili.objects.count(),
            'immobles_actius': Immoble.objects.filter(actiu=True).count(),
            'reserves_pagades': ReservaBasica.objects.filter(pagat=True).count(),
            'ingressos_totals': ReservaBasica.objects.aggregate(
                total=Sum('import_pagat')
            )['total'] or 0,
            'reserves_proximes_7_dies': ReservaBasica.objects.filter(
                data_entrada__range=[avui, avui + timedelta(days=7)]
            ).count(),
            'reserves_per_estat': reserves_per_estat,
            'ingressos_per_mes': ingressos_per_mes,
        }
        return Response(DashboardSerializer(data).data)
```

- [ ] **Step 3: Commit**

```bash
git add backend/bookings/views.py
git commit -m "feat(dashboard): add revenue, upcoming checkins and chart data to DashboardView"
```

---

## Task 3: Afegir RendimentPropietariView i URL

**Files:**
- Modify: `backend/bookings/views.py`
- Modify: `backend/bookings/urls.py`

- [ ] **Step 1: Afegir `RendimentPropietariView` al final de `views.py`**

Afegir just sota la classe `DashboardView`:

```python
class RendimentPropietariView(APIView):
    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        persona = get_object_or_404(Persona, pk=pk)
        if not hasattr(persona, 'perfil_propietari'):
            return Response(
                {'detail': 'Aquesta persona no és propietari.'},
                status=400,
            )

        from django.db.models import Count
        immobles = list(
            Immoble.objects
            .filter(propietari=persona)
            .annotate(
                num_reserves=Count('reserves'),
                ingressos_sum=Sum('reserves__import_pagat'),
            )
        )

        ingressos_totals = sum(float(i.ingressos_sum or 0) for i in immobles)

        return Response({
            'num_immobles': len(immobles),
            'immobles_actius': sum(1 for i in immobles if i.actiu),
            'total_reserves': sum(i.num_reserves for i in immobles),
            'ingressos_totals': f"{ingressos_totals:.2f}",
            'reserves_per_immoble': [
                {
                    'id': i.id,
                    'nom': i.nom_comercial,
                    'num_reserves': i.num_reserves,
                    'ingressos': f"{float(i.ingressos_sum or 0):.2f}",
                    'actiu': i.actiu,
                }
                for i in immobles
            ],
        })
```

- [ ] **Step 2: Afegir la ruta a `urls.py`**

Afegir al final de `urlpatterns` a `backend/bookings/urls.py`:

```python
path('persones/<int:pk>/rendiment/', views.RendimentPropietariView.as_view(), name='rendiment-propietari'),
```

- [ ] **Step 3: Escriure test per al nou endpoint**

Afegir a `backend/bookings/tests/test_persones.py`:

```python
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import Usuari
from bookings.models import Persona, PerfilPropietari, ReservaBasica
from properties.models import Immoble


class RendimentPropietariViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuari = Usuari.objects.create_user(nip='0001', password='test')
        self.client.force_authenticate(user=self.usuari)
        self.persona = Persona.objects.create(nom_complet='Prop Test', email='prop@test.com')
        PerfilPropietari.objects.create(persona=self.persona)
        self.immoble = Immoble.objects.create(
            nom_comercial='Pis Gràcia',
            adreca='C/ Test 1',
            preu_base_nit=100,
            propietari=self.persona,
            actiu=True,
        )
        inquili = Persona.objects.create(nom_complet='Inquilí Test')
        ReservaBasica.objects.create(
            immoble=self.immoble,
            inquili=inquili,
            data_entrada='2025-01-10',
            data_sortida='2025-01-15',
            import_pagat=500,
        )

    def test_retorna_rendiment_propietari(self):
        url = reverse('rendiment-propietari', args=[self.persona.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['num_immobles'], 1)
        self.assertEqual(data['immobles_actius'], 1)
        self.assertEqual(data['total_reserves'], 1)
        self.assertEqual(float(data['ingressos_totals']), 500.0)
        self.assertEqual(len(data['reserves_per_immoble']), 1)
        self.assertEqual(data['reserves_per_immoble'][0]['nom'], 'Pis Gràcia')

    def test_retorna_400_si_no_es_propietari(self):
        persona_sense_perfil = Persona.objects.create(nom_complet='No propietari')
        url = reverse('rendiment-propietari', args=[persona_sense_perfil.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 400)

    def test_retorna_404_si_persona_no_existeix(self):
        url = reverse('rendiment-propietari', args=[99999])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
```

- [ ] **Step 4: Executar tests**

```bash
cd backend && python manage.py test bookings.tests.test_persones -v 2
```

Expected: tots els tests passen.

- [ ] **Step 5: Commit**

```bash
git add backend/bookings/views.py backend/bookings/urls.py backend/bookings/tests/test_persones.py
git commit -m "feat(propietari): add RendimentPropietariView endpoint with tests"
```

---

## Task 4: Afegir `personesApi.rendiment` al client API

**Files:**
- Modify: `frontend/src/services/api.js`

- [ ] **Step 1: Afegir el mètode `rendiment` a `personesApi`**

Substituir el bloc `personesApi` existent (línies 96–102) per:

```js
export const personesApi = {
  list: () => api.get('/bookings/persones/'),
  get: (id) => api.get(`/bookings/persones/${id}/`),
  create: (data) => api.post('/bookings/persones/', data),
  update: (id, data) => api.patch(`/bookings/persones/${id}/`, data),
  remove: (id) => api.del(`/bookings/persones/${id}/`),
  rendiment: (id) => api.get(`/bookings/persones/${id}/rendiment/`),
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/services/api.js
git commit -m "feat(api): add personesApi.rendiment method"
```

---

## Task 5: Actualitzar DashboardPage (CSS + JSX)

**Files:**
- Modify: `frontend/src/components/pages/DashboardPage.module.css`
- Modify: `frontend/src/components/pages/DashboardPage.jsx`

- [ ] **Step 1: Substituir `DashboardPage.module.css` complet**

```css
.pageTitle {
  margin-bottom: 20px;
}

.pageTitle h2 {
  margin: 0;
  font-size: 1.8rem;
}

.pageTitle p {
  margin: 8px 0 0;
  color: #a1a1aa;
}

.dashboardGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
  margin-bottom: 28px;
}

.dashboardCard {
  background-color: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.dashboardCard:hover {
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.12);
  transform: translateY(-2px);
}

.dashboardCard h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1rem;
  color: #1e293b;
}

.metric {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2563eb;
  margin: 0 0 6px;
  line-height: 1;
}

.dashboardCard small {
  color: #64748b;
  font-size: 0.85rem;
}

/* Charts */

.chartsRow {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.chartCard {
  background-color: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 12px;
  padding: 20px;
}

.chartTitle {
  margin: 0 0 16px;
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
}

@media (max-width: 768px) {
  .chartsRow {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: Substituir `DashboardPage.jsx` complet**

```jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { bookingsApi } from '../../services/api';
import styles from './DashboardPage.module.css';

const ESTAT_COLORS = {
  prereservada: '#93c5fd',
  reservada: '#2563eb',
  lista: '#16a34a',
  cancelada: '#ef4444',
};

const ESTAT_LABELS = {
  prereservada: 'Prereservada',
  reservada: 'Reservada',
  lista: 'Lista',
  cancelada: 'Cancelada',
};

function formatEur(value) {
  return parseFloat(value || 0).toLocaleString('ca', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  });
}

function formatMes(mesStr) {
  const [year, month] = mesStr.split('-');
  const noms = ['Gen', 'Feb', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Des'];
  return `${noms[parseInt(month, 10) - 1]} ${year.slice(2)}`;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    bookingsApi
      .dashboard()
      .then(setStats)
      .catch((err) => setError(err.message));
  }, []);

  const estatData = stats
    ? Object.entries(stats.reserves_per_estat).map(([estat, count]) => ({
        estat: ESTAT_LABELS[estat] ?? estat,
        count,
        color: ESTAT_COLORS[estat] ?? '#94a3b8',
      }))
    : [];

  const mesData = stats?.ingressos_per_mes?.map((item) => ({
    mes: formatMes(item.mes),
    ingressos: parseFloat(item.ingressos || 0),
  })) ?? [];

  return (
    <section>
      <div className={styles.pageTitle}>
        <h2>Dashboard</h2>
        <p>Resumen general del sistema</p>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div className={styles.dashboardGrid}>
        <article
          className={styles.dashboardCard}
          onClick={() => navigate('/reserves')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/reserves')}
        >
          <h3>Reserves</h3>
          <p className={styles.metric}>{stats?.total_reserves ?? '—'}</p>
          <small>{stats ? `${stats.reserves_pagades} pagades` : 'Carregant...'}</small>
        </article>

        <article
          className={styles.dashboardCard}
          onClick={() => navigate('/inmobles')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/inmobles')}
        >
          <h3>Immobles</h3>
          <p className={styles.metric}>{stats?.total_immobles ?? '—'}</p>
          <small>{stats ? `${stats.immobles_actius} actius` : 'Carregant...'}</small>
        </article>

        <article
          className={styles.dashboardCard}
          onClick={() => navigate('/persones')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/persones')}
        >
          <h3>Persones</h3>
          <p className={styles.metric}>{stats?.total_inquilins ?? '—'}</p>
          <small>{stats ? 'Persones registrades' : 'Carregant...'}</small>
        </article>

        <article className={styles.dashboardCard} style={{ cursor: 'default' }}>
          <h3>Ingressos totals</h3>
          <p className={styles.metric}>
            {stats ? formatEur(stats.ingressos_totals) : '—'}
          </p>
          <small>Total cobrat</small>
        </article>

        <article className={styles.dashboardCard} style={{ cursor: 'default' }}>
          <h3>Properes entrades</h3>
          <p className={styles.metric}>{stats?.reserves_proximes_7_dies ?? '—'}</p>
          <small>Pròxims 7 dies</small>
        </article>
      </div>

      {stats && (
        <div className={styles.chartsRow}>
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Reserves per estat</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={estatData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                <XAxis dataKey="estat" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v) => [v, 'Reserves']} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {estatData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Ingressos mensuals (últims 6 mesos)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={mesData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(v) => `${v}€`} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => [`${parseFloat(v).toLocaleString('ca')} €`, 'Ingressos']} />
                <Bar dataKey="ingressos" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </section>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/pages/DashboardPage.jsx frontend/src/components/pages/DashboardPage.module.css
git commit -m "feat(dashboard): add revenue KPIs and recharts bar charts for RF-42"
```

---

## Task 6: Crear RendimentPropietariCard

**Files:**
- Create: `frontend/src/Cards/RendimentPropietariCard.jsx`
- Create: `frontend/src/Cards/RendimentPropietariCard.module.css`

- [ ] **Step 1: Crear `RendimentPropietariCard.module.css`**

```css
.section {
  padding: 0;
}

.section h2 {
  margin: 0 0 20px;
  font-size: 1.4rem;
  color: var(--text);
}

.kpiGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 14px;
  margin-bottom: 28px;
}

.kpiChip {
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kpiValue {
  font-size: 1.7rem;
  font-weight: 700;
  color: #2563eb;
  line-height: 1;
}

.kpiLabel {
  font-size: 0.8rem;
  color: #64748b;
}

.chartSection {
  margin-bottom: 28px;
}

.chartSection h3 {
  margin: 0 0 14px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
}

.immobleList h3 {
  margin: 0 0 12px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
}

.immobleRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 10px;
  margin-bottom: 8px;
}

.immobleNom {
  font-weight: 600;
  color: #2563eb;
  text-decoration: none;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.immobleNom:hover {
  text-decoration: underline;
}

.immobleStats {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  font-size: 0.88rem;
  color: #475569;
}

.badgeActiu {
  display: inline-block;
  background: #dcfce7;
  color: #15803d;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 20px;
}

.badgeInactiu {
  display: inline-block;
  background: #fee2e2;
  color: #b91c1c;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 20px;
}
```

- [ ] **Step 2: Crear `RendimentPropietariCard.jsx`**

```jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from 'recharts';
import { personesApi } from '../services/api';
import styles from './RendimentPropietariCard.module.css';

function formatEur(value) {
  return parseFloat(value || 0).toLocaleString('ca', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  });
}

export default function RendimentPropietariCard({ personaId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    personesApi
      .rendiment(personaId)
      .then(setData)
      .catch(() => setError("No s'han pogut carregar les dades de rendiment."))
      .finally(() => setLoading(false));
  }, [personaId]);

  if (loading) return <p>Carregant informe...</p>;
  if (error) return <p style={{ color: 'var(--danger, red)' }}>{error}</p>;
  if (!data) return null;

  const chartData = data.reserves_per_immoble.map((i) => ({
    nom: i.nom,
    ingressos: parseFloat(i.ingressos),
  }));

  return (
    <div className={styles.section}>
      <h2>Informes de rendiment</h2>

      <div className={styles.kpiGrid}>
        <div className={styles.kpiChip}>
          <span className={styles.kpiValue}>{data.num_immobles}</span>
          <span className={styles.kpiLabel}>Immobles totals</span>
        </div>
        <div className={styles.kpiChip}>
          <span className={styles.kpiValue}>{data.immobles_actius}</span>
          <span className={styles.kpiLabel}>Immobles actius</span>
        </div>
        <div className={styles.kpiChip}>
          <span className={styles.kpiValue}>{data.total_reserves}</span>
          <span className={styles.kpiLabel}>Reserves totals</span>
        </div>
        <div className={styles.kpiChip}>
          <span className={styles.kpiValue}>{formatEur(data.ingressos_totals)}</span>
          <span className={styles.kpiLabel}>Ingressos totals</span>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className={styles.chartSection}>
          <h3>Ingressos per immoble</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={chartData}
              margin={{ top: 8, right: 16, left: 0, bottom: 48 }}
            >
              <XAxis
                dataKey="nom"
                angle={-30}
                textAnchor="end"
                interval={0}
                tick={{ fontSize: 12 }}
              />
              <YAxis tickFormatter={(v) => `${v}€`} tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(v) => [`${parseFloat(v).toLocaleString('ca')} €`, 'Ingressos']}
              />
              <Bar dataKey="ingressos" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className={styles.immobleList}>
        <h3>Detall per immoble</h3>
        {data.reserves_per_immoble.length === 0 && (
          <p style={{ color: 'var(--muted)' }}>Aquest propietari no té immobles assignats.</p>
        )}
        {data.reserves_per_immoble.map((immoble) => (
          <div key={immoble.id} className={styles.immobleRow}>
            <Link to={`/inmobles/${immoble.id}`} className={styles.immobleNom}>
              {immoble.nom}
            </Link>
            <div className={styles.immobleStats}>
              <span>{immoble.num_reserves} reserves</span>
              <span>{parseFloat(immoble.ingressos).toLocaleString('ca')} €</span>
              <span className={immoble.actiu ? styles.badgeActiu : styles.badgeInactiu}>
                {immoble.actiu ? 'Actiu' : 'Inactiu'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/Cards/RendimentPropietariCard.jsx frontend/src/Cards/RendimentPropietariCard.module.css
git commit -m "feat(propietari): add RendimentPropietariCard component with KPIs and chart"
```

---

## Task 7: Actualitzar InfoPersonaPage amb layout Sidebar

**Files:**
- Modify: `frontend/src/components/pages/InfoPersonaPage.jsx`
- Modify: `frontend/src/components/pages/InfoPersonaPage.module.css`

- [ ] **Step 1: Afegir `.templateGrid` i `.perfilCard` a `InfoPersonaPage.module.css`**

Afegir al FINAL del fitxer existent (no substituir, afegir):

```css
.templateGrid {
  display: grid;
  grid-template-columns: 260px 1fr;
  align-items: start;
  min-height: 100vh;
}

.perfilCard {
  padding: 24px;
  min-width: 0;
}

@media (max-width: 900px) {
  .templateGrid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: Substituir `InfoPersonaPage.jsx` complet**

```jsx
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Sidebar from "../layout/Sidebar";
import FooterActions from "../layout/FooterActions";
import { personesApi, perfilsPropietariApi } from "../../services/api";
import PersonaFormSection from "./persones/PersonaFormSection";
import RendimentPropietariCard from "../../Cards/RendimentPropietariCard";
import styles from "./InfoPersonaPage.module.css";

const emptyPersona = {
  id: null,
  fullName: "",
  gender: "",
  documentType: "",
  documentNumber: "",
  nationality: "",
  birthDate: "",
  residence: "",
  email: "",
  phone: "",
  perfilPropietariId: null,
  fiscalName: "",
  fiscalId: "",
  billingAddress: "",
  billingPostalCode: "",
  billingCity: "",
  billingProvince: "",
  billingCountry: "",
  billingEmail: "",
  billingPhone: "",
  billingNotes: "",
};

function backendToForm(persona) {
  if (!persona) return emptyPersona;
  const p = persona.perfil_propietari;
  return {
    id: persona.id ?? null,
    fullName: persona.nom_complet ?? "",
    gender: persona.genere ?? "",
    documentType: persona.tipus_document ?? "",
    documentNumber: persona.dni_passaport ?? "",
    nationality: persona.nacionalitat ?? "",
    birthDate: persona.data_naixement ?? "",
    residence: persona.residencia ?? "",
    email: persona.email ?? "",
    phone: persona.telefon ?? "",
    perfilPropietariId: p?.id ?? null,
    fiscalName: p?.nom_fiscal ?? "",
    fiscalId: p?.nif_cif ?? "",
    billingAddress: p?.adreca_facturacio ?? "",
    billingPostalCode: p?.codi_postal_facturacio ?? "",
    billingCity: p?.ciutat_facturacio ?? "",
    billingProvince: p?.provincia_facturacio ?? "",
    billingCountry: p?.pais_facturacio ?? "",
    billingEmail: p?.email_facturacio ?? "",
    billingPhone: p?.telefon_facturacio ?? "",
    billingNotes: p?.observacions_facturacio ?? "",
  };
}

function personaToBackend(form) {
  return {
    nom_complet: form.fullName.trim(),
    genere: form.gender,
    tipus_document: form.documentType,
    dni_passaport: form.documentNumber.trim(),
    nacionalitat: form.nationality,
    data_naixement: form.birthDate || null,
    residencia: form.residence,
    email: form.email,
    telefon: form.phone,
  };
}

function perfilToBackend(form, personaId) {
  return {
    persona: personaId,
    nom_fiscal: form.fiscalName,
    nif_cif: form.fiscalId,
    adreca_facturacio: form.billingAddress,
    codi_postal_facturacio: form.billingPostalCode,
    ciutat_facturacio: form.billingCity,
    provincia_facturacio: form.billingProvince,
    pais_facturacio: form.billingCountry,
    email_facturacio: form.billingEmail,
    telefon_facturacio: form.billingPhone,
    observacions_facturacio: form.billingNotes,
  };
}

function hasBillingData(form) {
  return !!(
    form.fiscalName || form.fiscalId || form.billingAddress ||
    form.billingCity || form.billingEmail || form.billingNotes || form.billingPhone
  );
}

function validatePersona(form) {
  const errors = [];
  if (!form.fullName.trim()) errors.push("El nom complet és obligatori.");
  if (form.documentNumber.trim() && !form.documentType) {
    errors.push("El tipus de document és obligatori si introdueixes el número de document.");
  }
  if (form.documentType && !form.documentNumber.trim()) {
    errors.push("El número de document és obligatori si introdueixes el tipus de document.");
  }
  return errors;
}

export default function InfoPersonaPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id;

  const [seccioActiva, setSeccioActiva] = useState("perfil");
  const [isEditing, setIsEditing] = useState(isNew);
  const [persona, setPersona] = useState(emptyPersona);
  const [draftPersona, setDraftPersona] = useState(emptyPersona);
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isNew) {
      setPersona(emptyPersona);
      setDraftPersona(emptyPersona);
      setIsEditing(true);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    personesApi
      .get(id)
      .then((data) => {
        const mapped = backendToForm(data);
        setPersona(mapped);
        setDraftPersona(mapped);
      })
      .catch(() => setError("No s'han pogut carregar les dades de la persona."))
      .finally(() => setLoading(false));
  }, [id, isNew]);

  const seccions = useMemo(() => {
    const base = [{ id: "perfil", label: "Perfil" }];
    if (!isNew && persona.perfilPropietariId) {
      base.push({ id: "rendiment", label: "Informes de rendiment" });
    }
    return base;
  }, [isNew, persona.perfilPropietariId]);

  const currentPersona = isEditing ? draftPersona : persona;
  const title = useMemo(() => {
    if (isNew) return "Nova persona";
    return currentPersona.fullName || "Persona";
  }, [currentPersona.fullName, isNew]);

  const handleEdit = () => {
    setDraftPersona(persona);
    setIsEditing(true);
    setError("");
  };

  const handleCancel = () => {
    if (isNew) {
      navigate("/persones");
      return;
    }
    setDraftPersona(persona);
    setIsEditing(false);
    setError("");
  };

  const handleSave = async () => {
    const validationErrors = validatePersona(draftPersona);
    if (validationErrors.length) {
      setError(validationErrors[0]);
      return;
    }
    setSaving(true);
    setError("");
    try {
      const personaPayload = personaToBackend(draftPersona);
      const billingPresent = hasBillingData(draftPersona);
      let savedId;
      if (isNew) {
        const saved = await personesApi.create(personaPayload);
        savedId = saved.id;
      } else {
        await personesApi.update(id, personaPayload);
        savedId = Number(id);
      }
      if (billingPresent) {
        const perfilPayload = perfilToBackend(draftPersona, savedId);
        if (draftPersona.perfilPropietariId) {
          await perfilsPropietariApi.update(draftPersona.perfilPropietariId, perfilPayload);
        } else {
          await perfilsPropietariApi.create(perfilPayload);
        }
      }
      const full = await personesApi.get(savedId);
      const mapped = backendToForm(full);
      setPersona(mapped);
      setDraftPersona(mapped);
      setIsEditing(false);
      if (isNew) navigate(`/persones/${savedId}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setDraftPersona((prev) => ({ ...prev, [name]: value }));
  };

  if (loading) return <p>Carregant persona...</p>;

  return (
    <section>
      <div className={styles.templateGrid}>
        <Sidebar
          setSeccioActiva={setSeccioActiva}
          seccioActiva={seccioActiva}
          seccions={seccions}
        />

        <div className={styles.perfilCard}>
          <div className={styles.pageHeader}>
            <div>
              <h2>{title}</h2>
              <p>Gestió de dades personals, contacte i facturació</p>
            </div>
            <button
              type="button"
              className={styles.secondaryButton}
              onClick={() => navigate("/persones")}
            >
              Tornar
            </button>
          </div>

          {error && <p className={styles.error}>{error}</p>}

          {seccioActiva === "perfil" && (
            <>
              <PersonaFormSection
                data={currentPersona}
                isEditing={isEditing}
                onChange={handleChange}
              />
              <FooterActions
                isEditing={isEditing}
                onEdit={handleEdit}
                onCancel={handleCancel}
                onSave={handleSave}
                isSaveDisabled={saving}
                cancelLabel="Cancel·lar"
                saveLabel={saving ? "Guardant..." : "Guardar"}
              />
            </>
          )}

          {seccioActiva === "rendiment" && !isNew && persona.perfilPropietariId && (
            <RendimentPropietariCard personaId={id} />
          )}
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/pages/InfoPersonaPage.jsx frontend/src/components/pages/InfoPersonaPage.module.css
git commit -m "feat(persones): add sidebar layout with Rendiment tab for propietaris (RF-22)"
```
