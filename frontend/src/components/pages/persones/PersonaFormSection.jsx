import styles from "./PersonaFormSection.module.css";

function Field({
  label,
  name,
  value,
  isEditing,
  onChange,
  type = "text",
  options = null,
  textarea = false,
  fullWidth = false,
}) {
  return (
    <div className={`${styles.field} ${fullWidth ? styles.fullWidth : ""}`}>
      <label>{label}</label>

      {isEditing ? (
        options ? (
          <select name={name} value={value} onChange={onChange}>
            <option value="">Selecciona una opció</option>
            {options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        ) : textarea ? (
          <textarea name={name} value={value} onChange={onChange} rows="5" />
        ) : (
          <input name={name} type={type} value={value} onChange={onChange} />
        )
      ) : (
        <div className={textarea ? styles.textValue : styles.fieldValue}>
          {value || "-"}
        </div>
      )}
    </div>
  );
}

function FormBlock({ title, children }) {
  return (
    <section className={styles.block}>
      <div className={styles.blockHeader}>
        <h3>{title}</h3>
      </div>
      <div className={styles.formGrid}>{children}</div>
    </section>
  );
}

export default function PersonaFormSection({ data, isEditing, onChange }) {
  return (
    <div className={styles.card}>
      <FormBlock title="Dades personals i contacte">
        <Field
          label="Nom complet"
          name="fullName"
          value={data.fullName}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="Sexe"
          name="gender"
          value={data.gender}
          isEditing={isEditing}
          onChange={onChange}
          options={["Home", "Dona", "Altres"]}
        />
        <Field
          label="Tipus de document"
          name="documentType"
          value={data.documentType}
          isEditing={isEditing}
          onChange={onChange}
          options={["DNI", "NIE", "Passaport"]}
        />
        <Field
          label="Número de document"
          name="documentNumber"
          value={data.documentNumber}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="Nacionalitat"
          name="nationality"
          value={data.nationality}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="Data de naixement"
          name="birthDate"
          value={data.birthDate}
          isEditing={isEditing}
          onChange={onChange}
          type="date"
        />
        <Field
          label="Lloc de residència"
          name="residence"
          value={data.residence}
          isEditing={isEditing}
          onChange={onChange}
          fullWidth
        />
        <Field
          label="Correu electrònic"
          name="email"
          value={data.email}
          isEditing={isEditing}
          onChange={onChange}
          type="email"
        />
        <Field
          label="Telèfon"
          name="phone"
          value={data.phone}
          isEditing={isEditing}
          onChange={onChange}
          type="tel"
        />
      </FormBlock>

      <FormBlock title="Dades de facturació">
        <Field
          label="Nom fiscal"
          name="fiscalName"
          value={data.fiscalName}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="NIF / CIF"
          name="fiscalId"
          value={data.fiscalId}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="Adreça de facturació"
          name="billingAddress"
          value={data.billingAddress}
          isEditing={isEditing}
          onChange={onChange}
          fullWidth
        />
        <Field
          label="Codi postal"
          name="billingPostalCode"
          value={data.billingPostalCode}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="Ciutat"
          name="billingCity"
          value={data.billingCity}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="Província"
          name="billingProvince"
          value={data.billingProvince}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="País"
          name="billingCountry"
          value={data.billingCountry}
          isEditing={isEditing}
          onChange={onChange}
        />
        <Field
          label="Correu de facturació"
          name="billingEmail"
          value={data.billingEmail}
          isEditing={isEditing}
          onChange={onChange}
          type="email"
        />
        <Field
          label="Telèfon de facturació"
          name="billingPhone"
          value={data.billingPhone}
          isEditing={isEditing}
          onChange={onChange}
          type="tel"
        />
        <Field
          label="Observacions de facturació"
          name="billingNotes"
          value={data.billingNotes}
          isEditing={isEditing}
          onChange={onChange}
          textarea
          fullWidth
        />
      </FormBlock>
    </div>
  );
}
