import styles from "./ImmobiliariaInfoSection.module.css";

function Field({ label, name, value, isEditing, onChange, type = "text" }) {
  return (
    <div className={styles.field}>
      <label>{label}</label>

      {isEditing ? (
        <input name={name} type={type} value={value} onChange={onChange} />
      ) : (
        <div className={styles.fieldValue}>{value || "-"}</div>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <h2>{title}</h2>
      </div>
      <div className={styles.formGrid}>{children}</div>
    </section>
  );
}

export default function ImmobiliariaInfoSection({ data, isEditing, onChange }) {
  return (
    <div className={styles.profileForm}>
      <Section title="Dades generals">
        <Field
          label="Nom comercial"
          name="nomComercial"
          value={data.nomComercial}
          isEditing={isEditing}
          onChange={onChange}
        />

        <Field
          label="Raó social"
          name="raoSocial"
          value={data.raoSocial}
          isEditing={isEditing}
          onChange={onChange}
        />

        <Field
          label="NIF / CIF"
          name="nifCif"
          value={data.nifCif}
          isEditing={isEditing}
          onChange={onChange}
        />
      </Section>

      <Section title="Contacte">
        <Field
          label="Telèfon"
          name="telefon"
          value={data.telefon}
          isEditing={isEditing}
          onChange={onChange}
          type="tel"
        />

        <Field
          label="Correu electrònic"
          name="correuElectronic"
          value={data.correuElectronic}
          isEditing={isEditing}
          onChange={onChange}
          type="email"
        />

        <Field
          label="Web"
          name="web"
          value={data.web}
          isEditing={isEditing}
          onChange={onChange}
          type="url"
        />
      </Section>

      <Section title="Adreça fiscal">
        <div className={`${styles.field} ${styles.fullWidth}`}>
          <label>Adreça</label>
          {isEditing ? (
            <input name="adreca" value={data.adreca} onChange={onChange} />
          ) : (
            <div className={styles.fieldValue}>{data.adreca || "-"}</div>
          )}
        </div>

        <Field
          label="Codi postal"
          name="codiPostal"
          value={data.codiPostal}
          isEditing={isEditing}
          onChange={onChange}
        />

        <Field
          label="Ciutat"
          name="ciutat"
          value={data.ciutat}
          isEditing={isEditing}
          onChange={onChange}
        />

        <Field
          label="Província"
          name="provincia"
          value={data.provincia}
          isEditing={isEditing}
          onChange={onChange}
        />

        <Field
          label="País"
          name="pais"
          value={data.pais}
          isEditing={isEditing}
          onChange={onChange}
        />
      </Section>

      <Section title="Observacions">
        <div className={`${styles.field} ${styles.fullWidth}`}>
          <label>Observacions internes</label>
          {isEditing ? (
            <textarea
              name="observacionsInternes"
              value={data.observacionsInternes}
              onChange={onChange}
              rows="5"
            />
          ) : (
            <div className={styles.textValue}>
              {data.observacionsInternes || "-"}
            </div>
          )}
        </div>
      </Section>
    </div>
  );
}
