import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Calendar } from "@mantine/dates";
import dayjs from "dayjs";
import { bookingsApi } from "../services/api";
import styles from "./immobleCalendariCard.module.css";

const STATUS_COLORS = {
  prereservada: { bg: "#fef3c7", text: "#92400e", border: "#fcd34d", label: "Prereservada" },
  reservada:    { bg: "#dcfce7", text: "#166534", border: "#86efac", label: "Reservada" },
  lista:        { bg: "#dbeafe", text: "#1e40af", border: "#93c5fd", label: "Llesta" },
  cancelada:    { bg: "#f1f5f9", text: "#475569", border: "#cbd5e1", label: "Cancel·lada" },
};

export default function ImmobleCalendariCard({ immobleId, onFerReserva }) {
  const navigate = useNavigate();
  const [reserves, setReserves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedStart, setSelectedStart] = useState(null);
  const [selectedEnd, setSelectedEnd] = useState(null);

  useEffect(() => {
    if (!immobleId) return;
    setLoading(true);
    bookingsApi
      .listByImmoble(immobleId)
      .then((data) => {
        const all = data.results ?? data;
        setReserves(all.filter((r) => Number(r.immoble) === Number(immobleId)));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [immobleId]);

  // Mantine Calendar passes dates as "YYYY-MM-DD" strings to getDayProps
  function getReservaForDate(date) {
    return reserves.find((r) => date >= r.data_entrada && date <= r.data_sortida) ?? null;
  }

  function isInSelectedRange(date) {
    if (!selectedStart) return false;
    if (!selectedEnd) return date === selectedStart;
    return date >= selectedStart && date <= selectedEnd;
  }

  function handleDayClick(date) {
    const reserva = getReservaForDate(date);
    if (reserva) {
      navigate(`/infoReserva/${reserva.id}`);
      return;
    }

    if (!selectedStart || (selectedStart && selectedEnd)) {
      setSelectedStart(date);
      setSelectedEnd(null);
      return;
    }

    if (date === selectedStart) {
      setSelectedStart(null);
      setSelectedEnd(null);
    } else if (date < selectedStart) {
      setSelectedEnd(selectedStart);
      setSelectedStart(date);
    } else {
      setSelectedEnd(date);
    }
  }

  function getDayProps(date) {
    const reserva = getReservaForDate(date);

    if (reserva) {
      const colors = STATUS_COLORS[reserva.estat_reserva] ?? STATUS_COLORS.cancelada;
      return {
        style: { backgroundColor: colors.bg, color: colors.text, fontWeight: 600 },
        onClick: () => handleDayClick(date),
        title: `Reserva #${reserva.id}${reserva.inquili_nom ? ` — ${reserva.inquili_nom}` : ""}`,
      };
    }

    const inRange = isInSelectedRange(date);
    if (inRange) {
      const isEndpoint = date === selectedStart || date === selectedEnd;
      return {
        style: {
          backgroundColor: isEndpoint ? "#818cf8" : "#e0e7ff",
          color: isEndpoint ? "#fff" : "#312e81",
          fontWeight: isEndpoint ? 700 : 400,
        },
        onClick: () => handleDayClick(date),
      };
    }

    return { onClick: () => handleDayClick(date) };
  }

  const formatDate = (d) => (d ? dayjs(d).format("DD/MM/YYYY") : "");
  const canCreate = !!(selectedStart && selectedEnd);

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Calendari de reserves</h2>
            <p>Visualitza les reserves existents i selecciona un rang per crear-ne una de nova</p>
          </div>
        </div>

        {loading && <p className={styles.emptyState}>Carregant reserves...</p>}
        {error && <p className={styles.errorState}>{error}</p>}

        {!loading && !error && (
          <>
            <div className={styles.calendarWrapper}>
              <Calendar numberOfColumns={2} getDayProps={getDayProps} />
            </div>

            <div className={styles.legend}>
              {Object.entries(STATUS_COLORS).map(([key, val]) => (
                <span key={key} className={styles.legendItem}>
                  <span
                    className={styles.legendDot}
                    style={{ backgroundColor: val.bg, borderColor: val.border }}
                  />
                  {val.label}
                </span>
              ))}
            </div>

            {selectedStart && !selectedEnd && (
              <p className={styles.hint}>
                Data d&apos;entrada: <strong>{formatDate(selectedStart)}</strong> — Ara selecciona la data de sortida
              </p>
            )}

            {canCreate && (
              <div className={styles.selectionBar}>
                <div className={styles.selectionDates}>
                  <span>{formatDate(selectedStart)}</span>
                  <span className={styles.arrow}>→</span>
                  <span>{formatDate(selectedEnd)}</span>
                </div>
                <div className={styles.selectionActions}>
                  <button
                    className={styles.clearBtn}
                    onClick={() => { setSelectedStart(null); setSelectedEnd(null); }}
                  >
                    Netejar
                  </button>
                  <button
                    className={styles.ferReservaBtn}
                    onClick={() => onFerReserva(selectedStart, selectedEnd)}
                  >
                    Fer reserva
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}
