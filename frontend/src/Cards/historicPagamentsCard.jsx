import { useEffect, useState } from "react";
import { pagamentsApi } from "../services/api";
import styles from "./historicPagamentsCard.module.css";

const ESTAT_LABELS = {
  pagat:    "Pagat",
  pendent:  "Pendent",
  cancelat: "Cancel·lat",
};

const METODE_LABELS = {
  efectiu:       "Efectiu",
  transferencia: "Transferència",
  targeta:       "Targeta",
  bizum:         "Bizum",
  altres:        "Altres",
};

function formatDate(iso) {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

function formatImport(value) {
  return Number(value).toLocaleString("ca-ES", { minimumFractionDigits: 2 }) + " €";
}

export default function HistoricPagamentsCard({ immobleId }) {
  const [pagaments, setPagaments] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");

  useEffect(() => {
    if (!immobleId) return;
    setLoading(true);
    pagamentsApi
      .listByImmoble(immobleId)
      .then(setPagaments)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [immobleId]);

  const total = pagaments
    .filter((p) => p.estat === "pagat")
    .reduce((sum, p) => sum + Number(p.import_pagament), 0);

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Historial de pagaments</h2>
            <p>Registre dels cobres associats a les reserves d'aquest immoble</p>
          </div>
          {pagaments.length > 0 && (
            <div className={styles.totalBox}>
              <span className={styles.totalLabel}>Total cobrat</span>
              <span className={styles.totalValue}>{formatImport(total)}</span>
            </div>
          )}
        </div>

        {loading ? (
          <p className={styles.emptyState}>Carregant pagaments...</p>
        ) : error ? (
          <p className={styles.errorState}>{error}</p>
        ) : pagaments.length === 0 ? (
          <p className={styles.emptyState}>Encara no hi ha pagaments registrats per a aquest immoble.</p>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Reserva</th>
                  <th>Inquilí</th>
                  <th>Data</th>
                  <th>Import</th>
                  <th>Mètode</th>
                  <th>Estat</th>
                </tr>
              </thead>
              <tbody>
                {pagaments.map((p) => (
                  <tr key={p.id}>
                    <td className={styles.cellCode}>{p.codi_reserva}</td>
                    <td>{p.inquili_nom}</td>
                    <td className={styles.cellDate}>{formatDate(p.data_pagament)}</td>
                    <td className={styles.cellAmount}>{formatImport(p.import_pagament)}</td>
                    <td>{METODE_LABELS[p.metode_pagament] ?? p.metode_pagament}</td>
                    <td>
                      <span className={`${styles.badge} ${styles[`badge_${p.estat}`]}`}>
                        {ESTAT_LABELS[p.estat] ?? p.estat}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
