import styles from "./immobleDescompteCard.module.css";

function isDiscountActive(value) {
  return value === true || value === "true" || value === "Sí" || value === "Si";
}

function formatPercentatge(value, isActive) {
  if (!isActive) return "-";
  return value ? `${value}%` : "-";
}

function Field({
  label,
  value,
  name,
  isEditing,
  onChange,
  type = "text",
  options,
  displayValue,
  min,
  max,
}) {
  return (
    <div className={styles.field}>
      <label>{label}</label>

      {isEditing && options ? (
        <select name={name} value={value} onChange={onChange}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
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
        <div className={styles.fieldValue}>{displayValue ?? (value || "-")}</div>
      )}
    </div>
  );
}

export default function ImmobleDescompteCard({ data, isEditing, onChange }) {
  const descompteActiu = isDiscountActive(data.descompteActiu);
  const statusText = descompteActiu
    ? "Descompte actiu"
    : "Sense descompte actiu";

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Descompte</h2>
            <p>Configuració del descompte propi de l'immoble</p>
          </div>
        </div>

        <div className={styles.summaryBox}>
          <span
            className={`${styles.statusDot} ${
              descompteActiu ? styles.statusActive : styles.statusInactive
            }`}
            aria-hidden="true"
          />
          <span>{statusText}</span>
        </div>

        <div className={styles.formGrid}>
          <Field
            label="Descompte actiu"
            name="descompteActiu"
            value={String(descompteActiu)}
            isEditing={isEditing}
            onChange={onChange}
            displayValue={descompteActiu ? "Sí" : "No"}
            options={[
              { value: "true", label: "Sí" },
              { value: "false", label: "No" },
            ]}
          />

          <Field
            label="Percentatge de descompte"
            name="descomptePercentatge"
            value={data.descomptePercentatge}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
            min="0"
            max="100"
            displayValue={formatPercentatge(
              data.descomptePercentatge,
              descompteActiu
            )}
          />
        </div>
      </section>
    </div>
  );
}
