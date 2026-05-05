import styles from "./reservaPagamentsCard.module.css";

const DEFAULT_PAYMENT_STATUS = "pendent";

const PAYMENT_STATUS_LABELS = {
  pendent: "Pendent",
  parcial: "Parcial",
  pagada: "Pagada",
  retornada: "Retornada",
  rebutjada: "Rebutjada",
};

const PAYMENT_STATUS_CLASSES = {
  pendent: styles.statusPendent,
  parcial: styles.statusParcial,
  pagada: styles.statusPagada,
  retornada: styles.statusRetornada,
  rebutjada: styles.statusRebutjada,
};

const DEFAULT_PAYMENT_DATA = {
  estatPagament: DEFAULT_PAYMENT_STATUS,
  importTotal: "",
  importPagat: "",
  importPendent: "",
  fianca: "",
  metodePagament: "",
  dataUltimPagament: "",
  observacions: "Encara no hi ha pagaments registrats",
  descompteImmobleAplicat: false,
  descompteImmoblePercentatge: "",
  descompteIndividualAplicat: false,
  descompteIndividualPercentatge: "",
  descompteIndividualMotiu: "",
};

function toBoolean(value) {
  return value === true || value === "true" || value === "Sí" || value === "Si";
}

function formatBoolean(value) {
  return toBoolean(value) ? "Sí" : "No";
}

function formatPercentatge(value) {
  return value ? `${value}%` : "-";
}

function getPaymentStatusLabel(status) {
  return PAYMENT_STATUS_LABELS[status] ?? PAYMENT_STATUS_LABELS[DEFAULT_PAYMENT_STATUS];
}

function getPaymentStatusClass(status) {
  return PAYMENT_STATUS_CLASSES[status] ?? PAYMENT_STATUS_CLASSES[DEFAULT_PAYMENT_STATUS];
}

function Field({
  label,
  value,
  name,
  isEditing,
  onChange,
  type = "text",
  options,
  textarea = false,
  fullWidth = false,
  displayValue,
  min,
  max,
}) {
  return (
    <div className={`${styles.field} ${fullWidth ? styles.fullWidth : ""}`}>
      <label>{label}</label>

      {isEditing && options ? (
        <select name={name} value={value} onChange={onChange}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : isEditing && textarea ? (
        <textarea
          name={name}
          value={value}
          onChange={onChange}
          rows="5"
        />
      ) : isEditing ? (
        <input
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          min={min}
          max={max}
        />
      ) : (
        <div className={fullWidth ? styles.textValue : styles.fieldValue}>
          {displayValue ?? (value || "-")}
        </div>
      )}
    </div>
  );
}

export default function ReservaPagamentsCard({
  data = DEFAULT_PAYMENT_DATA,
  isEditing = false,
  onChange = () => {},
}) {
  const statusLabel = getPaymentStatusLabel(data.estatPagament);
  const statusClass = getPaymentStatusClass(data.estatPagament);
  const statusOptions = Object.entries(PAYMENT_STATUS_LABELS).map(
    ([value, label]) => ({ value, label })
  );
  const booleanOptions = [
    { value: "true", label: "Sí" },
    { value: "false", label: "No" },
  ];

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Pagaments</h2>
            <p>Resum econòmic i estat dels pagaments de la reserva</p>
          </div>
        </div>

        <div className={styles.paymentSummary}>
          <span
            className={`${styles.statusDot} ${statusClass}`}
            aria-hidden="true"
          />
          <span>{statusLabel}</span>
        </div>

        <div className={styles.formGrid}>
          <Field
            label="Estat del pagament"
            name="estatPagament"
            value={data.estatPagament}
            isEditing={isEditing}
            onChange={onChange}
            options={statusOptions}
            displayValue={statusLabel}
          />
          <Field
            label="Import total"
            name="importTotal"
            value={data.importTotal}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />
          <Field
            label="Import pagat"
            name="importPagat"
            value={data.importPagat}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />
          <Field
            label="Import pendent"
            name="importPendent"
            value={data.importPendent}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />
          <Field
            label="Fiança"
            name="fianca"
            value={data.fianca}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />
          <Field
            label="Mètode de pagament"
            name="metodePagament"
            value={data.metodePagament}
            isEditing={isEditing}
            onChange={onChange}
          />
          <Field
            label="Data últim pagament"
            name="dataUltimPagament"
            value={data.dataUltimPagament}
            isEditing={isEditing}
            onChange={onChange}
            type="date"
          />
          <Field
            label="Observacions"
            name="observacions"
            value={data.observacions}
            isEditing={isEditing}
            onChange={onChange}
            textarea
            fullWidth
          />
        </div>

        <div className={styles.sectionBlock}>
          <h3>Descomptes aplicats</h3>

          <div className={styles.formGrid}>
            <Field
              label="Descompte de l'immoble aplicat"
              name="descompteImmobleAplicat"
              value={String(toBoolean(data.descompteImmobleAplicat))}
              isEditing={isEditing}
              onChange={onChange}
              options={booleanOptions}
              displayValue={formatBoolean(data.descompteImmobleAplicat)}
            />
            <Field
              label="Percentatge descompte immoble"
              name="descompteImmoblePercentatge"
              value={data.descompteImmoblePercentatge}
              isEditing={isEditing}
              onChange={onChange}
              type="number"
              min="0"
              max="100"
              displayValue={formatPercentatge(data.descompteImmoblePercentatge)}
            />
            <Field
              label="Descompte individual aplicat"
              name="descompteIndividualAplicat"
              value={String(toBoolean(data.descompteIndividualAplicat))}
              isEditing={isEditing}
              onChange={onChange}
              options={booleanOptions}
              displayValue={formatBoolean(data.descompteIndividualAplicat)}
            />
            <Field
              label="Percentatge descompte individual"
              name="descompteIndividualPercentatge"
              value={data.descompteIndividualPercentatge}
              isEditing={isEditing}
              onChange={onChange}
              type="number"
              min="0"
              max="100"
              displayValue={formatPercentatge(data.descompteIndividualPercentatge)}
            />
            <Field
              label="Motiu del descompte"
              name="descompteIndividualMotiu"
              value={data.descompteIndividualMotiu}
              isEditing={isEditing}
              onChange={onChange}
              textarea
              fullWidth
            />
          </div>
        </div>
      </section>
    </div>
  );
}
