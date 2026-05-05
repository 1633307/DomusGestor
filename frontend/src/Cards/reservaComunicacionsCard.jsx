import styles from "./reservaComunicacionsCard.module.css";

const COMMUNICATION_STATUS_LABELS = {
  enviada: "Enviada",
  pendent: "Pendent",
  error: "Error",
  programada: "Programada",
};

const COMMUNICATION_STATUS_CLASSES = {
  enviada: styles.statusEnviada,
  pendent: styles.statusPendent,
  error: styles.statusError,
  programada: styles.statusProgramada,
};

const CHANNEL_OPTIONS = ["Email", "Telèfon", "WhatsApp", "Sistema"];

const STATUS_OPTIONS = [
  { value: "enviada", label: "Enviada" },
  { value: "pendent", label: "Pendent" },
  { value: "error", label: "Error" },
  { value: "programada", label: "Programada" },
];

function getStatusLabel(status) {
  return COMMUNICATION_STATUS_LABELS[status] ?? "Sense estat";
}

function getStatusClass(status) {
  return COMMUNICATION_STATUS_CLASSES[status] ?? styles.statusUnknown;
}

function Field({
  label,
  name,
  value,
  onChange,
  type = "text",
  options,
  textarea = false,
  fullWidth = false,
}) {
  return (
    <div className={`${styles.formField} ${fullWidth ? styles.fullWidth : ""}`}>
      <label>{label}</label>

      {options ? (
        <select name={name} value={value} onChange={onChange}>
          {options.map((option) => (
            <option key={option.value ?? option} value={option.value ?? option}>
              {option.label ?? option}
            </option>
          ))}
        </select>
      ) : textarea ? (
        <textarea
          name={name}
          value={value}
          onChange={onChange}
          rows="5"
        />
      ) : (
        <input
          name={name}
          type={type}
          value={value}
          onChange={onChange}
        />
      )}
    </div>
  );
}

export default function ReservaComunicacionsCard({
  comunicacions = [],
  draftComunicacio = {},
  isEditing = false,
  onDraftChange = () => {},
}) {
  const items = comunicacions;

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Comunicacions</h2>
            <p>Historial de missatges i avisos relacionats amb la reserva</p>
          </div>
        </div>

        {isEditing && (
          <div className={styles.newCommunicationForm}>
            <h3>Nova comunicació</h3>
            <div className={styles.formGrid}>
              <Field
                label="Canal"
                name="canal"
                value={draftComunicacio.canal}
                onChange={onDraftChange}
                options={CHANNEL_OPTIONS}
              />
              <Field
                label="Títol"
                name="titol"
                value={draftComunicacio.titol}
                onChange={onDraftChange}
              />
              <Field
                label="Destinatari"
                name="destinatari"
                value={draftComunicacio.destinatari}
                onChange={onDraftChange}
              />
              <Field
                label="Data"
                name="data"
                value={draftComunicacio.data}
                onChange={onDraftChange}
                type="date"
              />
              <Field
                label="Estat"
                name="estat"
                value={draftComunicacio.estat}
                onChange={onDraftChange}
                options={STATUS_OPTIONS}
              />
              <Field
                label="Resum"
                name="resum"
                value={draftComunicacio.resum}
                onChange={onDraftChange}
                textarea
                fullWidth
              />
            </div>
          </div>
        )}

        {items.length === 0 ? (
          <div className={styles.emptyState}>
            Encara no hi ha comunicacions registrades
          </div>
        ) : (
          <div className={styles.communicationList}>
            {items.map((comunicacio) => (
              <article className={styles.communicationItem} key={comunicacio.id}>
                <div className={styles.itemHeader}>
                  <div>
                    <h3>{comunicacio.titol}</h3>
                    <p>{comunicacio.canal}</p>
                  </div>

                  <div className={styles.statusBadge}>
                    <span
                      className={`${styles.statusDot} ${getStatusClass(
                        comunicacio.estat
                      )}`}
                      aria-hidden="true"
                    />
                    <span>{getStatusLabel(comunicacio.estat)}</span>
                  </div>
                </div>

                <div className={styles.metaGrid}>
                  <div className={styles.metaField}>
                    <span>Destinatari</span>
                    <strong>{comunicacio.destinatari || "-"}</strong>
                  </div>
                  <div className={styles.metaField}>
                    <span>Data</span>
                    <strong>{comunicacio.data || "-"}</strong>
                  </div>
                </div>

                <p className={styles.summary}>{comunicacio.resum || "-"}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
