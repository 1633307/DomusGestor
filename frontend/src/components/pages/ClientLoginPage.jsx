import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { clientPortalApi } from '../../services/api';
import styles from './clientLoginPage.module.css';

const RESERVA_STATUS_LABELS = {
  prereservada: 'Prereservada',
  reservada: 'Reservada',
  lista: 'Llesta',
  cancelada: 'Cancel·lada',
};

const PAYMENT_STATUS_LABELS = {
  pendent: 'Pendent',
  parcial: 'Parcial',
  pagada: 'Pagada',
  retornada: 'Retornada',
  rebutjada: 'Rebutjada',
};

const PAYMENT_STATUS_CLASSES = {
  pendent: styles.paymentPendent,
  parcial: styles.paymentParcial,
  pagada: styles.paymentPagada,
  retornada: styles.paymentRetornada,
  rebutjada: styles.paymentRebutjada,
};

function formatDate(value) {
  if (!value) return '-';
  return new Intl.DateTimeFormat('ca-ES', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(new Date(value));
}

function formatCurrency(value) {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat('ca-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(Number.isFinite(amount) ? amount : 0);
}

function getReservaStatusLabel(status) {
  return RESERVA_STATUS_LABELS[status] ?? 'Sense estat';
}

function getPaymentStatusLabel(status) {
  return PAYMENT_STATUS_LABELS[status] ?? PAYMENT_STATUS_LABELS.pendent;
}

function getPaymentStatusClass(status) {
  return PAYMENT_STATUS_CLASSES[status] ?? PAYMENT_STATUS_CLASSES.pendent;
}

function SummaryField({ label, value }) {
  const displayValue = value === undefined || value === null || value === '' ? '-' : value;

  return (
    <div className={styles.summaryField}>
      <span>{label}</span>
      <strong>{displayValue}</strong>
    </div>
  );
}

export default function ClientLoginPage() {
  const [form, setForm] = useState({
    codiReserva: '',
    nip: '',
  });
  const [reserva, setReserva] = useState(null);
  const [paymentFormVisible, setPaymentFormVisible] = useState(false);
  const [visualPaymentDone, setVisualPaymentDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [paymentError, setPaymentError] = useState('');

  const paymentInfo = useMemo(() => {
    if (!reserva) return null;
    const paid = visualPaymentDone || reserva.estat_pagament === 'pagada';
    const status = paid ? 'pagada' : reserva.estat_pagament || 'pendent';
    return {
      paid,
      status,
      importPagat: paid ? reserva.import_total : reserva.import_pagat,
      importPendent: paid ? 0 : reserva.import_pendent,
    };
  }, [reserva, visualPaymentDone]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const data = await clientPortalApi.login(form.codiReserva, form.nip);
      setReserva(data);
      setPaymentFormVisible(false);
      setVisualPaymentDone(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleFakePayment = async (e) => {
    e.preventDefault();
    setPaymentError('');
    setSubmitting(true);
    try {
      const data = await clientPortalApi.pay(form.codiReserva, form.nip);
      setReserva(data);
      setPaymentFormVisible(false);
      setVisualPaymentDone(true);
    } catch (err) {
      setPaymentError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (reserva && paymentInfo) {
    return (
      <section className={styles.portalPage}>
        <header className={styles.portalHeader}>
          <div>
            <p className={styles.loginTag}>Portal clients</p>
            <h1>Reserva {reserva.codi_reserva || `#${reserva.id}`}</h1>
            <p>{reserva.immoble_nom}</p>
          </div>
          <button
            type="button"
            className={styles.secondaryButton}
            onClick={() => setReserva(null)}
          >
            Consultar una altra reserva
          </button>
        </header>

        <main className={styles.portalGrid}>
          <section className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <h2>Informació de la reserva</h2>
                <p>Dades principals de l'estada</p>
              </div>
              <span className={styles.statusBadge}>
                {getReservaStatusLabel(reserva.estat_reserva)}
              </span>
            </div>

            <div className={styles.summaryGrid}>
              <SummaryField label="Client" value={reserva.inquili_nom} />
              <SummaryField label="Entrada" value={formatDate(reserva.data_entrada)} />
              <SummaryField label="Sortida" value={formatDate(reserva.data_sortida)} />
              <SummaryField label="Hostes" value={reserva.num_hostes} />
              <SummaryField label="Tipus" value={reserva.tipus_reserva} />
              <SummaryField label="Fiança" value={formatCurrency(reserva.fianca)} />
            </div>

            {reserva.hostes?.length > 0 && (
              <div className={styles.guestBlock}>
                <h3>Hostes registrats</h3>
                <div className={styles.guestList}>
                  {reserva.hostes.map((hoste) => (
                    <span key={hoste.id}>
                      {hoste.nom_complet}
                      {hoste.es_principal ? ' · principal' : ''}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>

          <section className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <h2>Pagament</h2>
                <p>Resum econòmic de la reserva</p>
              </div>
              <span
                className={`${styles.paymentBadge} ${getPaymentStatusClass(paymentInfo.status)}`}
              >
                {getPaymentStatusLabel(paymentInfo.status)}
              </span>
            </div>

            <div className={styles.paymentTotals}>
              <SummaryField label="Total" value={formatCurrency(reserva.import_total)} />
              <SummaryField label="Pagat" value={formatCurrency(paymentInfo.importPagat)} />
              <SummaryField label="Pendent" value={formatCurrency(paymentInfo.importPendent)} />
              <SummaryField label="Últim pagament" value={formatDate(reserva.data_ultim_pagament)} />
            </div>

            {reserva.observacions_pagament && (
              <p className={styles.paymentNote}>{reserva.observacions_pagament}</p>
            )}

            {!paymentInfo.paid && !paymentFormVisible && (
              <button
                type="button"
                className={styles.primaryButton}
                onClick={() => setPaymentFormVisible(true)}
              >
                Realitzar pagament
              </button>
            )}

            {paymentFormVisible && (
              <form className={styles.paymentForm} onSubmit={handleFakePayment}>
                <label>
                  Nom a la targeta
                  <input type="text" placeholder="Nom i cognoms" required />
                </label>
                <label>
                  Número de targeta
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="0000 0000 0000 0000"
                    required
                  />
                </label>
                <div className={styles.paymentFormRow}>
                  <label>
                    Caducitat
                    <input type="text" placeholder="MM/AA" required />
                  </label>
                  <label>
                    CVC
                    <input type="text" inputMode="numeric" placeholder="000" required />
                  </label>
                </div>
                {paymentError && <p className={styles.errorText}>{paymentError}</p>}
                <div className={styles.paymentActions}>
                  <button type="submit" className={styles.primaryButton} disabled={submitting}>
                    {submitting ? 'Processant...' : 'Confirmar pagament'}
                  </button>
                  <button
                    type="button"
                    className={styles.secondaryButton}
                    onClick={() => setPaymentFormVisible(false)}
                    disabled={submitting}
                  >
                    Cancel·lar
                  </button>
                </div>
              </form>
            )}

            {visualPaymentDone && (
              <p className={styles.successText}>Pagament confirmat correctament. La reserva ha estat actualitzada.</p>
            )}
          </section>
        </main>
      </section>
    );
  }

  return (
    <section className={styles.loginPage}>
      <div className={styles.loginBox}>
        <div className={styles.loginHeader}>
          <p className={styles.loginTag}>Portal clients</p>
          <h1 className={styles.title}>Accés a la teva reserva</h1>
          <p className={styles.loginSubtitle}>
            Consulta la informació de la teva estada i l'estat del pagament.
          </p>
        </div>

        <form className={styles.loginForm} onSubmit={handleSubmit}>
          <label className={styles.field}>
            Número de reserva
            <input
              className={styles.input}
              type="text"
              name="codiReserva"
              value={form.codiReserva}
              onChange={handleChange}
              placeholder="Ex. RES-2026-0001"
            />
          </label>

          <label className={styles.field}>
            NIP
            <input
              className={styles.input}
              type="text"
              name="nip"
              value={form.nip}
              onChange={handleChange}
              placeholder="Introdueix el teu NIP"
            />
          </label>

          {error && <p className={styles.errorText}>{error}</p>}

          <button type="submit" className={styles.primaryButton} disabled={submitting}>
            {submitting ? 'Verificant...' : 'Accedir'}
          </button>
        </form>

        <div className={styles.loginFooter}>
          <Link to="/login">Tornar a l'accés de gestió</Link>
        </div>
      </div>
    </section>
  );
}
