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

export default function PerfilCard({ data, isEditing, onChange }) {
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

          <div className={`${styles.field} ${styles.fullWidth}`}>
            <label>Foto principal</label>

            {!isEditing ? (
              <div className={styles.imagePreview}>
                {data.mainPhoto ? (
                  <img src={data.mainPhoto} alt="Foto principal de l'immoble" />
                ) : (
                  <div className={styles.emptyImage}>Sense imatge</div>
                )}
              </div>
            ) : (
              <input
                name="mainPhoto"
                value={data.mainPhoto}
                onChange={onChange}
              />
            )}
          </div>
        </div>
      </section>

      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Informació del propietari</h2>
            <p>Dades personals i fiscals del propietari vinculat</p>
          </div>
        </div>

        <div className={styles.formGrid}>
          <Field
            label="Nom complet"
            name="ownerName"
            value={data.ownerName}
            isEditing={isEditing}
            onChange={onChange}
          />

          <Field
            label="DNI / NIF"
            name="ownerTaxId"
            value={data.ownerTaxId}
            isEditing={isEditing}
            onChange={onChange}
          />

          <Field
            label="Email"
            name="ownerEmail"
            value={data.ownerEmail}
            isEditing={isEditing}
            onChange={onChange}
            type="email"
          />

          <Field
            label="Telèfon"
            name="ownerPhone"
            value={data.ownerPhone}
            isEditing={isEditing}
            onChange={onChange}
          />

          <div className={`${styles.field} ${styles.fullWidth}`}>
            <label>Adreça fiscal</label>
            {isEditing ? (
              <input
                name="ownerAddress"
                value={data.ownerAddress}
                onChange={onChange}
              />
            ) : (
              <div className={styles.fieldValue}>{data.ownerAddress || "-"}</div>
            )}
          </div>

          <div className={`${styles.field} ${styles.fullWidth}`}>
            <label>IBAN</label>
            {isEditing ? (
              <input
                name="ownerIban"
                value={data.ownerIban}
                onChange={onChange}
              />
            ) : (
              <div className={styles.fieldValue}>{data.ownerIban || "-"}</div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}