import { useState } from "react";
import { useParams } from "react-router-dom";
import { portalApi } from "../../services/api";
import styles from "./PortalReservaPage.module.css";

const STATUS_LABELS = {
  prereservada: "Pendent de confirmacio",
  reservada: "Reserva confirmada",
  lista: "Check-in completat",
  cancelada: "Reserva cancel.lada",
};

const EMPTY_GUEST = {
  es_principal: false,
  nom_complet: "",
  genere: "",
  relacio_parental: "",
  tipus_document: "DNI",
  numero_document: "",
  nacionalitat: "",
  data_naixement: "",
  residencia: "",
  email: "",
  telefon: "",
};

function money(value) {
  return `${Number(value || 0).toFixed(2)} EUR`;
}

function reservationStatusLabel(status) {
  return STATUS_LABELS[status] ?? "Pendent de confirmacio";
}

function formatHours(start, end) {
  if (!start && !end) return "A confirmar";
  return [start?.slice(0, 5), end?.slice(0, 5)].filter(Boolean).join(" - ");
}

function normalizeGuests(hostes) {
  if (hostes?.length) {
    return hostes.map((hoste, index) => ({
      ...EMPTY_GUEST,
      ...hoste,
      es_principal: index === 0,
      data_naixement: hoste.data_naixement ?? "",
    }));
  }
  return [{ ...EMPTY_GUEST, es_principal: true }];
}

export default function PortalReservaPage() {
  const { codiReserva } = useParams();
  const [document, setDocument] = useState("");
  const [reserva, setReserva] = useState(null);
  const [hostes, setHostes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const updateReserva = (data) => {
    setReserva(data);
    setHostes(normalizeGuests(data.hostes));
  };

  const withAction = async (action) => {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await action();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAccess = (event) => {
    event.preventDefault();
    withAction(async () => {
      const data = await portalApi.access(codiReserva, document);
      updateReserva(data);
    });
  };

  const handlePayment = () => {
    withAction(async () => {
      const data = await portalApi.pay(codiReserva, document);
      updateReserva(data);
      setMessage("Pagament simulat correctament. La reserva ja esta confirmada.");
    });
  };

  const handleGuestChange = (index, field, value) => {
    setHostes((current) =>
      current.map((hoste, position) =>
        position === index ? { ...hoste, [field]: value } : hoste,
      ),
    );
  };

  const addGuest = () => setHostes((current) => [...current, { ...EMPTY_GUEST }]);

  const removeGuest = (index) => {
    setHostes((current) => current.filter((_, position) => position !== index));
  };

  const handleCheckin = (event) => {
    event.preventDefault();
    withAction(async () => {
      const data = await portalApi.checkin(codiReserva, document, hostes);
      updateReserva(data);
      setMessage("Check-in completat. Les dades dels hostes han quedat registrades.");
    });
  };

  const canPay = reserva && reserva.estat_reserva !== "cancelada" &&
    (!reserva.pagat || !["reservada", "lista"].includes(reserva.estat_reserva));
  const canCheckin = reserva?.estat_reserva === "reservada" && reserva?.pagat;

  if (!reserva) {
    return (
      <main className={styles.authPage}>
        <section className={styles.authCard}>
          <p className={styles.eyebrow}>Portal del client</p>
          <h1>Consulta la teva reserva</h1>
          <p className={styles.intro}>
            Introdueix el document de l'hoste principal per accedir al check-in i al pagament.
          </p>
          <p className={styles.bookingCode}>Reserva: {codiReserva}</p>
          <form onSubmit={handleAccess}>
            <label htmlFor="document">DNI, NIE o passaport</label>
            <input
              id="document"
              value={document}
              onChange={(event) => setDocument(event.target.value)}
              placeholder="12345678A"
              required
            />
            {error && <p className={styles.error}>{error}</p>}
            <button type="submit" disabled={loading}>
              {loading ? "Comprovant..." : "Accedir a la reserva"}
            </button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.portal}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Portal del client</p>
          <h1>{reserva.immoble_nom}</h1>
          <p>{reserva.immoble_adreca}</p>
        </div>
        <span className={`${styles.status} ${styles[reserva.estat_reserva]}`}>
          {reservationStatusLabel(reserva.estat_reserva)}
        </span>
      </header>

      {message && <p className={styles.success}>{message}</p>}
      {error && <p className={styles.errorBanner}>{error}</p>}

      <section className={styles.summary}>
        <article>
          <span>Estada</span>
          <strong>{reserva.data_entrada} - {reserva.data_sortida}</strong>
        </article>
        <article>
          <span>Arribada</span>
          <strong>{formatHours(reserva.hora_checkin_inici, reserva.hora_checkin_fi)}</strong>
        </article>
        <article>
          <span>Sortida</span>
          <strong>{formatHours(reserva.hora_checkout_inici, reserva.hora_checkout_fi)}</strong>
        </article>
      </section>

      <section className={styles.payment}>
        <div>
          <p className={styles.eyebrow}>Pagament</p>
          <h2>{reserva.pagat ? "Pagament completat" : "Pagament pendent"}</h2>
          <p>
            Total {money(reserva.import_total)} · Pagat {money(reserva.import_pagat)} ·
            Pendent {money(reserva.import_pendent)}
          </p>
        </div>
        {canPay && (
          <button type="button" onClick={handlePayment} disabled={loading}>
            {reserva.pagat ? "Confirmar reserva" : "Pagar ara (demo)"}
          </button>
        )}
      </section>

      {![ "reservada", "lista", "cancelada" ].includes(reserva.estat_reserva) && (
        <p className={styles.notice}>
          Completa el pagament per confirmar la reserva i habilitar el check-in online.
        </p>
      )}

      {canCheckin && (
        <form className={styles.checkin} onSubmit={handleCheckin}>
          <div className={styles.checkinHeader}>
            <div>
              <p className={styles.eyebrow}>Check-in online</p>
              <h2>Dades dels viatgers</h2>
              <p>Completa les dades de totes les persones que s'allotjaran.</p>
            </div>
            <button type="button" className={styles.secondary} onClick={addGuest}>
              Afegir hoste
            </button>
          </div>
          {hostes.map((hoste, index) => (
            <fieldset key={index} className={styles.guest}>
              <legend>{index === 0 ? "Hoste principal" : `Hoste ${index + 1}`}</legend>
              {index > 0 && (
                <button
                  type="button"
                  className={styles.remove}
                  onClick={() => removeGuest(index)}
                >
                  Eliminar
                </button>
              )}
              <div className={styles.grid}>
                <GuestInput label="Nom complet" value={hoste.nom_complet} onChange={(value) => handleGuestChange(index, "nom_complet", value)} required />
                <GuestSelect label="Genere" value={hoste.genere} onChange={(value) => handleGuestChange(index, "genere", value)} options={["", "Home", "Dona", "Altres"]} />
                <GuestSelect label="Tipus de document" value={hoste.tipus_document} onChange={(value) => handleGuestChange(index, "tipus_document", value)} options={["DNI", "NIE", "Passaport"]} required />
                <GuestInput label="Numero de document" value={hoste.numero_document} onChange={(value) => handleGuestChange(index, "numero_document", value)} required />
                <GuestInput label="Nacionalitat" value={hoste.nacionalitat} onChange={(value) => handleGuestChange(index, "nacionalitat", value)} required />
                <GuestInput label="Data de naixement" type="date" value={hoste.data_naixement} onChange={(value) => handleGuestChange(index, "data_naixement", value)} required />
                <GuestInput label="Residencia habitual" value={hoste.residencia} onChange={(value) => handleGuestChange(index, "residencia", value)} required />
                <GuestInput label="Email" type="email" value={hoste.email} onChange={(value) => handleGuestChange(index, "email", value)} />
                <GuestInput label="Telefon" value={hoste.telefon} onChange={(value) => handleGuestChange(index, "telefon", value)} />
                {index > 0 && (
                  <GuestInput label="Relacio amb menor" value={hoste.relacio_parental} onChange={(value) => handleGuestChange(index, "relacio_parental", value)} />
                )}
              </div>
            </fieldset>
          ))}
          <button type="submit" disabled={loading}>
            {loading ? "Desant..." : "Finalitzar check-in"}
          </button>
        </form>
      )}

      {reserva.estat_reserva === "lista" && (
        <section className={styles.completed}>
          <h2>Check-in completat</h2>
          <p>Les dades de {reserva.hostes.length} hoste(s) ja consten a la reserva.</p>
        </section>
      )}
    </main>
  );
}

function GuestInput({ label, value, onChange, type = "text", required = false }) {
  return (
    <label>
      {label}
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        required={required}
      />
    </label>
  );
}

function GuestSelect({ label, value, onChange, options, required = false }) {
  return (
    <label>
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)} required={required}>
        {options.map((option) => <option key={option} value={option}>{option || "Selecciona"}</option>)}
      </select>
    </label>
  );
}
