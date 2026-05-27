import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import styles from "./page.module.css";
import { bookingsApi } from "../../../services/api";

function Event({ type, event }) {
  return (
    <Link
      className={`${styles.event} ${styles[type]}`}
      to={"/infoReserva/" + event.immoble}
    >
      <span className={styles.eventTitle}>
        <i
          className={
            "fa-solid " +
            (type === "entrada"
              ? "fa-arrow-right-to-bracket"
              : "fa-arrow-right-from-bracket")
          }
        />
        &nbsp;{type === "entrada" ? "Entrada" : "Sortida"}
      </span>
      <span className={styles.nomImmoble}>{event.immoble_nom}</span>
      <span className={styles.nomHoste}>
        <i className="fa-solid fa-user" />&nbsp;{event.inquili_nom}
        {event.hostes.length > 1 ? ` +${event.hostes.length - 1} més` : ""}
      </span>
    </Link>
  );
}

export default function Page() {
  const [date, setDate] = useState(new Date());
  const [data, setData] = useState();

  useEffect(() => {
    bookingsApi.list().then(setData).catch(console.error);
  }, []);

  const moveDate = (days) =>
    setDate((d) => new Date(d.getTime() + days * 24 * 60 * 60 * 1000));

  const moveMonth = (months) =>
    setDate((d) => {
      const nd = new Date(d);
      nd.setMonth(nd.getMonth() + months);
      return nd;
    });

  const moveYear = (years) =>
    setDate((d) => {
      const nd = new Date(d);
      nd.setFullYear(nd.getFullYear() + years);
      return nd;
    });

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Calendari</h2>
          <p>Entrades i sortides dels pròxims dies</p>
        </div>

        <div className={styles.navControls}>
          <div className={styles.navGroup}>
            <button onClick={() => moveYear(-1)} title="Recular un any" className={styles.navBtn}>
              <i className="fa-solid fa-angles-left" /> Any
            </button>
            <button onClick={() => moveMonth(-1)} title="Recular un mes" className={styles.navBtn}>
              <i className="fa-solid fa-chevron-left" /> Mes
            </button>
            <button onClick={() => moveDate(-1)} title="Recular un dia" className={styles.navBtn}>
              <i className="fa-solid fa-chevron-left" /> Dia
            </button>
          </div>

          <button onClick={() => setDate(new Date())} className={styles.todayBtn}>
            Avui
          </button>

          <div className={styles.navGroup}>
            <button onClick={() => moveDate(1)} title="Avançar un dia" className={styles.navBtn}>
              Dia <i className="fa-solid fa-chevron-right" />
            </button>
            <button onClick={() => moveMonth(1)} title="Avançar un mes" className={styles.navBtn}>
              Mes <i className="fa-solid fa-chevron-right" />
            </button>
            <button onClick={() => moveYear(1)} title="Avançar un any" className={styles.navBtn}>
              Any <i className="fa-solid fa-angles-right" />
            </button>
          </div>
        </div>
      </div>

      <div className={styles.daysContainer}>
        {[-1, 0, 1, 2, 3].map((diff) => {
          const newDate = new Date(date.getTime() + diff * 24 * 60 * 60 * 1000);
          const newDateString =
            newDate.getFullYear() +
            "-" +
            String(newDate.getMonth() + 1).padStart(2, "0") +
            "-" +
            String(newDate.getDate()).padStart(2, "0");

          const entrades = data
            ?.filter((e) => e.data_entrada === newDateString)
            .toSorted((a, b) => (a.data_entrada < b.data_entrada ? -1 : 1));
          const sortides = data
            ?.filter((e) => e.data_sortida === newDateString)
            .toSorted((a, b) => (a.data_sortida < b.data_sortida ? -1 : 1));

          return (
            <div
              className={`${styles.day} ${diff === 0 ? styles.dayToday : ""}`}
              key={diff}
            >
              <div className={styles.dayHeader}>
                {Intl.DateTimeFormat("ca", {
                  weekday: "short",
                  day: "numeric",
                  month: "short",
                }).format(newDate)}
              </div>

              <div className={styles.events}>
                {data ? (
                  <>
                    {entrades.map((event) => (
                      <Event key={`e-${event.id}`} type="entrada" event={event} />
                    ))}
                    {sortides.map((event) => (
                      <Event key={`s-${event.id}`} type="sortida" event={event} />
                    ))}
                    {entrades.length === 0 && sortides.length === 0 && (
                      <span className={styles.emptyDay}>—</span>
                    )}
                  </>
                ) : (
                  <span className={styles.emptyDay}>Carregant...</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
