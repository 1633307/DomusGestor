import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { bookingsApi } from '../../services/api';
import styles from './inmoblesPage.module.css';

export default function ReservesPage() {
  const [reserves, setReserves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    bookingsApi
      .list()
      .then((data) => setReserves(data.results ?? data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <h2>Llistat Reserves</h2>
      </div>

      <div className={styles.Toolbar}>
        <input
          type="text"
          placeholder="Buscar reserva"
          className={styles.searchInput}
        />
      </div>

      {loading && <p>Carregant...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div className={styles.Grid}>
        {reserves.map((reserva) => (
          <article className={styles.Card} key={reserva.id}>
            <Link to={`/infoReserva/${reserva.id}`}>
              <h3>Reserva #{reserva.id}</h3>
              <p>{reserva.immoble_nom} — {reserva.inquili_nom}</p>
              <p>{reserva.data_entrada} → {reserva.data_sortida}</p>
              <p>{reserva.pagat ? 'Pagada' : 'Pendent'}</p>
            </Link>
          </article>
        ))}
        {!loading && reserves.length === 0 && <p>No hi ha reserves.</p>}
      </div>
    </section>
  );
}
