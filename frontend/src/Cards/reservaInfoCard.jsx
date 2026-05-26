import styles from "./reservaInfoCard.module.css";

function Field({
  label,
  value,
  name,
  isEditing,
  onChange,
  type = "text",
  editable = true,
  options,
  displayValue,
}) {
  const canEdit = isEditing && editable;

  return (
    <div className={styles.field}>
      <label>{label}</label>

      {canEdit && options ? (
        <select name={name} value={value} onChange={onChange}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : canEdit ? (
        <input
          name={name}
          type={type}
          value={value}
          onChange={onChange}
        />
      ) : (
        <div className={styles.fieldValue}>{displayValue ?? (value || "-")}</div>
      )}
    </div>
  );
}

function formatLimpio(value) {
  return value === true || value === "true" || value === "Sí" || value === "Si"
    ? "Sí"
    : "No";
}

function getLimpioSelectValue(value) {
  return formatLimpio(value) === "Sí" ? "true" : "false";
}

export default function ReservaInfoCard({ data, isEditing, onChange }) {
  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Informació de la reserva</h2>
            <p>Dades generals de la reserva seleccionada</p>
          </div>
        </div>

        <div className={styles.formGrid}>
          {/* Editable */}
          <Field
            label="Número d'hostes"
            name="guestCount"
            value={data.guestCount}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
            editable={true}
          />

          {/* Bloqueado */}
          <Field
            label="Codi de la reserva"
            name="reservationCode"
            value={data.reservationCode}
            isEditing={isEditing}
            onChange={onChange}
            editable={false}
          />

          {/* Bloqueado */}
          <Field
            label="Data d'entrada"
            name="startDate"
            value={data.startDate}
            isEditing={isEditing}
            onChange={onChange}
            type="date"
            editable={false}
          />

          {/* Bloqueado */}
          <Field
            label="Data de sortida"
            name="endDate"
            value={data.endDate}
            isEditing={isEditing}
            onChange={onChange}
            type="date"
            editable={false}
          />

          {/* Bloqueado */}
          <Field
            label="Immoble reservat"
            name="reservedProperty"
            value={data.reservedProperty}
            isEditing={isEditing}
            onChange={onChange}
            editable={false}
          />

          {/* Bloqueado */}
          <div className={styles.field}>
            <label>Tipus de reserva</label>
            <div className={styles.fieldValue}>
              {data.reservationType || "-"}
            </div>
          </div>

          {/* Editable */}
          <Field
            label="Estat de la reserva"
            name="estadoReserva"
            value={data.estadoReserva}
            isEditing={isEditing}
            onChange={onChange}
            options={[
              { value: "", label: "-" },
              { value: "prereservada", label: "Prereservada" },
              { value: "reservada", label: "Reservada" },
              { value: "lista", label: "Llesta" },
              { value: "cancelada", label: "Cancel·lada" },
            ]}
          />

          {/* Editable */}
          <Field
            label="Net"
            name="limpio"
            value={getLimpioSelectValue(data.limpio)}
            isEditing={isEditing}
            onChange={onChange}
            displayValue={formatLimpio(data.limpio)}
            options={[
              { value: "true", label: "Sí" },
              { value: "false", label: "No" },
            ]}
          />

          {/* Editable */}
          <Field
            label="Hores extra de neteja"
            name="limpiezaExtra"
            value={data.limpiezaExtra}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />

          {/* Editable */}
          <div className={`${styles.field} ${styles.fullWidth}`}>
            <label>Comentaris interns</label>

            {isEditing ? (
              <textarea
                name="internalComments"
                value={data.internalComments}
                onChange={onChange}
                rows="5"
              />
            ) : (
              <div className={styles.textValue}>
                {data.internalComments || "-"}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
