import { useState } from "react";
import styles from "./netegesCard.module.css";

export default function NetegesCard() {

  const [obertura, setObertura] = useState("");
  const [tancament, setTancament] = useState("");
  const [canvi, setCanvi] = useState("");
  const [nReserves, setNReserves] = useState("0");

  
  const total = 
    (Number(obertura) || 0) + 
    (Number(tancament) || 0) + 
    (Number(canvi) || 0) * (Number(nReserves) || 0)

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Temps de neteja</h2>
            <p>Configura les hores estimades per a cada tipus d'intervenció</p>
          </div>
          <div className={styles.totalBox}>
            <span className={styles.totalLabel}>TOTAL HORES EN {nReserves} reserves</span>
            <span className={styles.totalValue}>{total} h</span>
          </div>
        </div>

        <div className={styles.formGrid}>
          <div className={styles.inputGroup}>
            <label htmlFor="obertura">Obertura</label>
            <div className={styles.inputWrapper}>
              <input
                id="obertura"
                type="number"
                min="0"
                step="0.5"
                placeholder="Ex: 2.5"
                value={obertura}
                onChange={(e) => setObertura(e.target.value)}
                className={styles.input}
              />
              <span className={styles.inputSuffix}>h</span>
            </div>
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="tancament">Tancament</label>
            <div className={styles.inputWrapper}>
              <input
                id="tancament"
                type="number"
                min="0"
                step="0.5"

                value={tancament}
                onChange={(e) => setTancament(e.target.value)}
                className={styles.input}
              />
              <span className={styles.inputSuffix}>h</span>
            </div>
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="canvi">Canvi (Turnover)</label>
            <div className={styles.inputWrapper}>
              <input
                id="canvi"
                type="number"
                min="0"
                step="0.5"
                placeholder="Ex: 1.5"
                value={canvi}
                onChange={(e) => setCanvi(e.target.value)}
                className={styles.input}
              />
              <span className={styles.inputSuffix}>h</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}