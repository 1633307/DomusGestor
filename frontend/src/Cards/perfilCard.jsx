import PropietariSelector from "../components/forms/PropietariSelector";
import styles from "./perfilCard.module.css";

function Field({ label, value, name, isEditing, onChange, type = "text" }) {
  return (
    <div className={styles.field}>
      <label>{label}</label>

      {isEditing ? (
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

export default function PerfilCard({ data, isEditing, onChange, onPropietariChange }) {
  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Informació de l'immoble</h2>
            <p>Dades generals i tècniques de l'immoble</p>
          </div>
        </div>

        <div className={styles.formGrid}>
          <Field
            label="Nom de l'immoble"
            name="propertyName"
            value={data.propertyName}
            isEditing={isEditing}
            onChange={onChange}
          />

          <Field
            label="Referència"
            name="reference"
            value={data.reference}
            isEditing={isEditing}
            onChange={onChange}
          />

          <div className={`${styles.field} ${styles.fullWidth}`}>
            <label>Adreça</label>
            {isEditing ? (
              <input
                name="address"
                value={data.address}
                onChange={onChange}
              />
            ) : (
              <div className={styles.fieldValue}>{data.address || "-"}</div>
            )}
          </div>

          <Field
            label="Ciutat"
            name="city"
            value={data.city}
            isEditing={isEditing}
            onChange={onChange}
          />

          <Field
            label="Codi postal"
            name="postalCode"
            value={data.postalCode}
            isEditing={isEditing}
            onChange={onChange}
          />

          <Field
            label="Tipus d'immoble"
            name="propertyType"
            value={data.propertyType}
            isEditing={isEditing}
            onChange={onChange}
          />

          <Field
            label="Capacitat"
            name="capacity"
            value={data.capacity}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />

          <Field
            label="Habitacions"
            name="bedrooms"
            value={data.bedrooms}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />

          <Field
            label="Banys"
            name="bathrooms"
            value={data.bathrooms}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />

          <Field
            label="Preu base"
            name="basePrice"
            value={data.basePrice}
            isEditing={isEditing}
            onChange={onChange}
            type="number"
          />
        </div>
      </section>

      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Informació del propietari</h2>
            <p>Dades personals i fiscals del propietari vinculat</p>
          </div>
        </div>

        <PropietariSelector
          propietariId={data.propietariId}
          propietariData={{
            ownerName: data.ownerName,
            ownerEmail: data.ownerEmail,
            ownerPhone: data.ownerPhone,
            ownerTaxId: data.ownerTaxId,
            ownerAddress: data.ownerAddress,
            ownerIban: data.ownerIban,
          }}
          isEditing={isEditing}
          onChange={onPropietariChange}
        />
      </section>
    </div>
  );
}
