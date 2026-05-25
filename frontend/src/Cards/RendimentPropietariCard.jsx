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
