import { useEffect, useState } from "react";

import styles from "./page.module.css";
import { bookingsApi } from "../../../services/api";

function Event({ type, event }) {
  return (
    <div className={styles["event"] + " " + styles[type]}>
      <span className={styles["title"]}>
        <i
          class={
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
    </div>
  );
}

export default function Page() {
  // Hard-coded for testing
  const [date, setDate] = useState(new Date("2026-07-11"));
  const [data, setData] = useState();

  useEffect(() => {
    bookingsApi.list().then(setData).catch(console.error);
  }, []);

  useEffect(() => console.log(data), [data]);

  return (
    <div>
      <h1 className={styles["title"]}>Calendari</h1>

      <div className={styles["days-container"]}>
        {/* Ahir, avui, demà, demà-passat i el següent */}
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
                {diff === 0 && <span className={styles["today"]}>Avui</span>}
                <span className={styles["date"]}>
                  {Intl.DateTimeFormat("ca", {
                    weekday: "long",
                    day: "numeric",
                    month: "long",
                  }).format(newDate)}
                </span>
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
