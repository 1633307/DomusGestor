import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { bookingsApi } from '../../services/api';
import styles from './DashboardPage.module.css';

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
          <h3>Reservas</h3>
          <p className={styles.metric}>{stats?.total_reserves ?? '—'}</p>
          <small>{stats ? `${stats.reserves_pagades} pagades` : 'Cargando...'}</small>
        </article>

        <article
          className={styles.dashboardCard}
          onClick={() => navigate('/inmobles')}
          style={{ cursor: 'pointer' }}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/inmobles')}
        >
          <h3>Inmobles</h3>
          <p className={styles.metric}>{stats?.total_immobles ?? '—'}</p>
          <small>{stats ? `${stats.immobles_actius} actius` : 'Cargando...'}</small>
        </article>

        <article className={styles.dashboardCard}>
          <h3>Clientes</h3>
          <p className={styles.metric}>{stats?.total_inquilins ?? '—'}</p>
          <small>{stats ? 'Inquilins registrats' : 'Cargando...'}</small>
        </article>
      </div>
    </section>
  );
}
