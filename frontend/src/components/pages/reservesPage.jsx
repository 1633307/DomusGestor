import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { bookingsApi } from '../../services/api';
import styles from './reservesPage.module.css';

const RESERVA_STATUS_LABELS = {
  prereservada: 'Prereservada',
  reservada: 'Reservada',
  lista: 'Llesta',
  cancelada: 'Cancel·lada',
};

const RESERVA_STATUS_CLASSES = {
  prereservada: styles.statusPrereservada,
  reservada: styles.statusReservada,
  lista: styles.statusLista,
  cancelada: styles.statusCancelada,
};

function getReservaStatusValue(reserva) {
  return String(
    reserva.estat_reserva ?? reserva.estadoReserva ?? reserva.estado_reserva ?? ''
  )
    .trim()
    .toLowerCase();
}

function getReservaStatusLabel(status) {
  return RESERVA_STATUS_LABELS[status] ?? 'Sense estat';
}

function getReservaStatusClass(status) {
  return RESERVA_STATUS_CLASSES[status] ?? styles.statusUnknown;
}

export default function ReservesPage() {
  const [reserves, setReserves] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    bookingsApi
      .list()
      .then((data) => setReserves(data.results ?? data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const filteredReserves = reserves.filter((reserva) => {
    const q = search.toLowerCase();
    return (
      String(reserva.id).includes(q) ||
      (reserva.immoble_nom ?? '').toLowerCase().includes(q) ||
      (reserva.inquili_nom ?? '').toLowerCase().includes(q)
    );
  });

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Llistat Reserves</h2>
          <p>Gestiona i consulta totes les reserves registrades</p>
        </div>
      </div>

      <div className={styles.reservesToolbar}>
        <input
          type="text"
          placeholder="Cercar reserves..."
          className={styles.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading && <p className={styles.stateMsg}>Carregant...</p>}
      {error && <p className={styles.errorMsg}>{error}</p>}

      <div className={styles.reservesGrid}>
        {filteredReserves.map((reserva) => {
          const status = getReservaStatusValue(reserva);
          return (
            <Link
              to={`/infoReserva/${reserva.id}`}
              key={reserva.id}
              className={styles.reservaCardLink}
            >
              <article
                className={`${styles.reservaCard} ${styles[`card_${status}`] ?? ''}`}
              >
                <div className={styles.cardInfo}>
                  <h3>Reserva #{reserva.id}</h3>
                  <p className={styles.cardSub}>
                    {reserva.immoble_nom} — {reserva.inquili_nom}
                  </p>
                  <p className={styles.cardDates}>
                    {reserva.data_entrada} → {reserva.data_sortida}
                  </p>
                </div>
                <div className={styles.cardFooter}>
                  <span
                    className={`${styles.statusBadge} ${getReservaStatusClass(status)}`}
                  >
                    {getReservaStatusLabel(status)}
                  </span>
                  <span
                    className={`${styles.paymentBadge} ${reserva.pagat ? styles.paymentPagat : styles.paymentPendent}`}
                  >
                    {reserva.pagat ? 'Pagada' : 'Pendent'}
                  </span>
                </div>
              </article>
            </Link>
          );
        })}
        {!loading && filteredReserves.length === 0 && (
          <p className={styles.stateMsg}>No hi ha reserves.</p>
        )}
      </div>
    </section>
  );
}
