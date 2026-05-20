import styles from "./horarisCard.module.css";

function formatHora(value) {
  if (!value) return "No definit";
  return value.slice(0, 5);
}

export default function HorarisCard({ data, isEditing, onChange }) {
  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <h2>Horaris d'entrada i sortida</h2>
          <p>Configura el rang d'hores de check-in i check-out de l'immoble</p>
        </div>

        <div className={styles.blocksGrid}>
          <div className={styles.block}>
            <div className={styles.blockTitle}>Check-in</div>
            <div className={styles.rangeRow}>
              <div className={styles.field}>
                <label>De</label>
                {isEditing ? (
                  <input
                    type="time"
                    name="horaCheckinInici"
                    value={data.horaCheckinInici ?? ""}
                    onChange={onChange}
                  />
                ) : (
                  <div className={styles.fieldValue}>{formatHora(data.horaCheckinInici)}</div>
                )}
              </div>
              <span className={styles.separator}>–</span>
              <div className={styles.field}>
                <label>Fins</label>
                {isEditing ? (
                  <input
                    type="time"
                    name="horaCheckinFi"
                    value={data.horaCheckinFi ?? ""}
                    onChange={onChange}
                  />
                ) : (
                  <div className={styles.fieldValue}>{formatHora(data.horaCheckinFi)}</div>
                )}
              </div>
            </div>
          </div>

          <div className={styles.block}>
            <div className={styles.blockTitle}>Check-out</div>
            <div className={styles.rangeRow}>
              <div className={styles.field}>
                <label>De</label>
                {isEditing ? (
                  <input
                    type="time"
                    name="horaCheckoutInici"
                    value={data.horaCheckoutInici ?? ""}
                    onChange={onChange}
                  />
                ) : (
                  <div className={styles.fieldValue}>{formatHora(data.horaCheckoutInici)}</div>
                )}
              </div>
              <span className={styles.separator}>–</span>
              <div className={styles.field}>
                <label>Fins</label>
                {isEditing ? (
                  <input
                    type="time"
                    name="horaCheckoutFi"
                    value={data.horaCheckoutFi ?? ""}
                    onChange={onChange}
                  />
                ) : (
                  <div className={styles.fieldValue}>{formatHora(data.horaCheckoutFi)}</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
