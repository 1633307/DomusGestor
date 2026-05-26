import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import styles from "./page.module.css";
import { bookingsApi } from "../../../services/api";

function Event({ type, event }) {
  return (
    <Link
      className={styles["event"] + " " + styles[type]}
      to={"/infoReserva/" + event.immoble}
    >
      <span className={styles["title"]}>
        <i
          className={
            "fa-solid" +
            " " +
            (type === "entrada"
              ? "fa-arrow-right-to-bracket"
              : "fa-arrow-right-from-bracket")
          }
        ></i>
        &nbsp;{type === "entrada" ? "Entrada" : "Sortida"}
      </span>
      <span className={styles["nom-immoble"]}>{event.immoble_nom}</span>
      <span className={styles["nom-hoste"]}>
        <i className="fa-solid fa-user"></i>&nbsp;{event.inquili_nom}{" "}
        {event.hostes.length > 1 ? `+${event.hostes.length - 1} més` : ""}
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

  return (
    <div className={styles["wrapper"]}>
      <div className={styles["page-header"]}>
        <h1>Calendari</h1>
        <div className={styles["buttons"]}>
          <button
            onClick={() => {
              const newDate = new Date(date);
              newDate.setFullYear(newDate.getFullYear() - 1);
              setDate(newDate);
            }}
            title="Recular un any"
          >
            <i className="fa-solid fa-chevron-left"></i>
            <span>Any</span>
          </button>
          <button
            onClick={() => {
              const newDate = new Date(date);
              newDate.setMonth(newDate.getMonth() - 1);
              setDate(newDate);
            }}
            title="Recular un mes"
          >
            <i className="fa-solid fa-chevron-left"></i>
            <span>Mes</span>
          </button>
          <button
            onClick={() =>
              setDate((date) => new Date(date.getTime() - 24 * 60 * 60 * 1000))
            }
            title="Recular un dia"
          >
            <i className="fa-solid fa-chevron-left"></i>
            <span>Dia</span>
          </button>
          <button
            onClick={() =>
              setDate((date) => new Date(date.getTime() + 24 * 60 * 60 * 1000))
            }
            title="Avançar un dia"
          >
            <i className="fa-solid fa-chevron-right"></i>
            <span>Dia</span>
          </button>
          <button
            onClick={() => {
              const newDate = new Date(date);
              newDate.setMonth(newDate.getMonth() + 1);
              setDate(newDate);
            }}
            title="Avançar un mes"
          >
            <i className="fa-solid fa-chevron-right"></i>
            <span>Mes</span>
          </button>
          <button
            onClick={() => {
              const newDate = new Date(date);
              newDate.setFullYear(newDate.getFullYear() + 1);
              setDate(newDate);
            }}
            title="Avançar un any"
          >
            <i className="fa-solid fa-chevron-right"></i>
            <span>Any</span>
          </button>
        </div>
      </div>

      <div className={styles["days-container"]}>
        {/* Ahir, avui, demà, demà-passat i el següent respecte del dia triat */}
        {[-1, 0, 1, 2, 3].map((diff) => {
          const newDate = new Date(date.getTime() + diff * 24 * 60 * 60 * 1000);
          const newDateString =
            newDate.getFullYear() +
            "-" +
            (newDate.getMonth() + 1 < 10 ? "0" : "") +
            (newDate.getMonth() + 1) +
            "-" +
            (newDate.getDate() < 10 ? "0" : "") +
            newDate.getDate();

          const entrades = data
            ?.filter((e) => e.data_entrada === newDateString)
            .toSorted((a, b) =>
              a.data_entrada < b.data_entrada
                ? -1
                : a.data_entrada > b.data_entrada
                  ? 1
                  : 0,
            );
          const sortides = data
            ?.filter((e) => e.data_sortida === newDateString)
            .toSorted((a, b) =>
              a.data_sortida < b.data_sortida
                ? -1
                : a.data_sortida > b.data_sortida
                  ? 1
                  : 0,
            );

          return (
            <div className={styles["day"]} key={diff}>
              <div className={styles["header"]}>
                {Intl.DateTimeFormat("ca", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                }).format(newDate)}
              </div>

              <div className={styles["events"]}>
                {data ? (
                  entrades.map((event) => (
                    <Event type="entrada" event={event} />
                  ))
                ) : (
                  <>Carregant...</>
                )}
                {data ? (
                  sortides.map((event) => (
                    <Event type="sortida" event={event} />
                  ))
                ) : (
                  <></>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
