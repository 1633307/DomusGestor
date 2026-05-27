import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend,
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

  const estatData = stats?.reserves_per_estat
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

  const pagamentData = stats
    ? [
        { name: 'Pagades', value: stats.reserves_pagades, color: '#16a34a' },
        { name: 'Pendents', value: stats.total_reserves - stats.reserves_pagades, color: '#f59e0b' },
      ]
    : [];

  const immobleData = stats
    ? [
        { name: 'Actius', value: stats.immobles_actius, color: '#2563eb' },
        { name: 'Inactius', value: stats.total_immobles - stats.immobles_actius, color: '#94a3b8' },
      ]
    : [];

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    if (percent < 0.05) return null;
    const RADIAN = Math.PI / 180;
    const r = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + r * Math.cos(-midAngle * RADIAN);
    const y = cy + r * Math.sin(-midAngle * RADIAN);
    return (
      <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={13} fontWeight={600}>
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

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
          style={{ cursor: 'pointer' }}
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
          style={{ cursor: 'pointer' }}
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
          style={{ cursor: 'pointer' }}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/persones')}
        >
          <h3>Persones</h3>
          <p className={styles.metric}>{stats?.total_inquilins ?? '—'}</p>
          <small>{stats ? 'Persones registrades' : 'Carregant...'}</small>
        </article>

        <article className={styles.dashboardCard}>
          <h3>Ingressos totals</h3>
          <p className={styles.metric}>
            {stats ? formatEur(stats.ingressos_totals) : '—'}
          </p>
          <small>Total cobrat</small>
        </article>

        <article className={styles.dashboardCard}>
          <h3>Properes entrades</h3>
          <p className={styles.metric}>{stats?.reserves_proximes_7_dies ?? '—'}</p>
          <small>Pròxims 7 dies</small>
        </article>
      </div>

      {(estatData.length > 0 || mesData.length > 0) && (
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

      {stats && (
        <div className={styles.chartsRow} style={{ marginTop: 18 }}>
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Pagament de reserves</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pagamentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                  labelLine={false}
                  label={renderCustomLabel}
                >
                  {pagamentData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(v, name) => [v, name]} />
                <Legend iconType="circle" iconSize={10} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Estat dels immobles</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={immobleData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                  labelLine={false}
                  label={renderCustomLabel}
                >
                  {immobleData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(v, name) => [v, name]} />
                <Legend iconType="circle" iconSize={10} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </section>
  );
}
