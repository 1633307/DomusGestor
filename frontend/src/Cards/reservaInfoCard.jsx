import styles from "./reservaInfoCard.module.css";

function Field({
  label,
  value,
  name,
  isEditing,
  onChange,
  type = "text",
  editable = true,
}) {
  const canEdit = isEditing && editable;

  return (
    <div className={styles.field}>
      <label>{label}</label>

      {canEdit ? (
        <input
          name={name}
          type={type}
          value={value}
          onChange={onChange}
        />
      ) : (
        <div className={styles.fieldValue}>{value || "-"}</div>
      )}
    </div>
  );
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