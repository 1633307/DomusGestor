import { useEffect, useState } from 'react';
import { api } from '../../../services/api';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboard()
      .then(setStats)
      .catch((err) => console.error('Error cargando dashboard:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Cargando...</p>;

  return (
    <section>
      <div className="page-title">
        <h2>Dashboard</h2>
        <p>Resumen general del sistema</p>
      </div>

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <h3>Reservas</h3>
          <p className="dashboard-stat">{stats?.total_reserves ?? 0}</p>
          <p>{stats?.reserves_confirmades ?? 0} confirmadas</p>
        </article>

        <article className="dashboard-card">
          <h3>Inmuebles</h3>
          <p className="dashboard-stat">{stats?.total_immobles ?? 0}</p>
          <p>{stats?.immobles_actius ?? 0} activos</p>
        </article>

        <article className="dashboard-card">
          <h3>Clientes</h3>
          <p className="dashboard-stat">{stats?.total_inquilins ?? 0}</p>
        </article>
      </div>
    </section>
  );
}
