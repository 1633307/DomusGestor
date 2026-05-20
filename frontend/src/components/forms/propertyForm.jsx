import { useState } from 'react';
import styles from './PropertyForm.module.css';

const emptyForm = {
  propertyName: '',
  reference: '',
  address: '',
  city: '',
  postalCode: '',
  propertyType: '',
  squareMeters: '',
  capacity: '',
  bedrooms: '',
  bathrooms: '',
  basePrice: '',
  ownerName: '',
  ownerTaxId: '',
  ownerEmail: '',
  ownerPhone: '',
  ownerAddress: '',
  ownerIban: '',
};

const BACKEND_FIELD_MAP = {
  nom_comercial: 'propertyName',
  referencia: 'reference',
  adreca: 'address',
  ciutat: 'city',
  codi_postal: 'postalCode',
  tipus_immoble: 'propertyType',
  metres_quadrats: 'squareMeters',
  capacitat_maxima: 'capacity',
  num_habitacions: 'bedrooms',
  num_banys: 'bathrooms',
  preu_base_nit: 'basePrice',
  propietari_nom: 'ownerName',
  propietari_dni: 'ownerTaxId',
  propietari_email: 'ownerEmail',
  propietari_telefon: 'ownerPhone',
  propietari_adreca: 'ownerAddress',
  propietari_iban: 'ownerIban',
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isPositiveInt(val) {
  if (val === '' || val === null || val === undefined) return true;
  const n = Number(val);
  return Number.isInteger(n) && n >= 0;
}

function validate(form) {
  const errors = {};

  // Camps obligatoris (model: no blank)
  if (!form.propertyName.trim())
    errors.propertyName = "El nom de l'immoble és obligatori.";
  else if (form.propertyName.length > 100)
    errors.propertyName = "El nom no pot superar els 100 caràcters.";

  if (!form.address.trim())
    errors.address = "L'adreça és obligatòria.";

  // Preu base: ha de ser un número vàlid i no negatiu
  if (form.basePrice !== '' && isNaN(Number(form.basePrice)))
    errors.basePrice = 'El preu base ha de ser un número.';
  else if (form.basePrice !== '' && Number(form.basePrice) < 0)
    errors.basePrice = 'El preu base no pot ser negatiu.';

  // Camps numèrics enters positius
  if (!isPositiveInt(form.squareMeters))
    errors.squareMeters = 'Els metres quadrats han de ser un número enter positiu.';
  if (!isPositiveInt(form.capacity))
    errors.capacity = 'La capacitat màxima ha de ser un número enter positiu.';
  if (!isPositiveInt(form.bedrooms))
    errors.bedrooms = 'El número d\'habitacions ha de ser un enter positiu.';
  if (!isPositiveInt(form.bathrooms))
    errors.bathrooms = 'El número de banys ha de ser un enter positiu.';

  // Email del propietari
  if (form.ownerEmail && !EMAIL_RE.test(form.ownerEmail))
    errors.ownerEmail = "El format de l'email no és vàlid.";

  // Longituds màximes del model
  if (form.reference.length > 50)
    errors.reference = 'La referència no pot superar els 50 caràcters.';
  if (form.city.length > 100)
    errors.city = 'La ciutat no pot superar els 100 caràcters.';
  if (form.postalCode.length > 10)
    errors.postalCode = 'El codi postal no pot superar els 10 caràcters.';
  if (form.propertyType.length > 50)
    errors.propertyType = 'El tipus d\'immoble no pot superar els 50 caràcters.';
  if (form.ownerName.length > 150)
    errors.ownerName = 'El nom no pot superar els 150 caràcters.';
  if (form.ownerTaxId.length > 20)
    errors.ownerTaxId = 'El DNI/NIF no pot superar els 20 caràcters.';
  if (form.ownerPhone.length > 30)
    errors.ownerPhone = 'El telèfon no pot superar els 30 caràcters.';
  if (form.ownerIban.length > 34)
    errors.ownerIban = "L'IBAN no pot superar els 34 caràcters.";

  return errors;
}

function formToBackend(f) {
  return {
    nom_comercial: f.propertyName,
    referencia: f.reference,
    adreca: f.address,
    ciutat: f.city,
    codi_postal: f.postalCode,
    tipus_immoble: f.propertyType,
    metres_quadrats: Number(f.squareMeters) || 0,
    capacitat_maxima: Number(f.capacity) || 0,
    num_habitacions: Number(f.bedrooms) || 0,
    num_banys: Number(f.bathrooms) || 0,
    preu_base_nit: Number(f.basePrice) || 0,
    propietari_nom: f.ownerName,
    propietari_dni: f.ownerTaxId,
    propietari_email: f.ownerEmail,
    propietari_telefon: f.ownerPhone,
    propietari_adreca: f.ownerAddress,
    propietari_iban: f.ownerIban,
    descompte_actiu: false,
    descompte_percentatge: 0,
    temporades: [],
    serveis: [],
  };
}

export default function PropertyForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const clientErrors = validate(form);
    if (Object.keys(clientErrors).length > 0) {
      setFieldErrors(clientErrors);
      return;
    }

    setSubmitting(true);
    setError('');
    setFieldErrors({});

    try {
      await onSubmit(formToBackend(form));
    } catch (err) {
      if (err.fieldErrors) {
        const mapped = {};
        for (const [backendKey, messages] of Object.entries(err.fieldErrors)) {
          const formKey = BACKEND_FIELD_MAP[backendKey] ?? backendKey;
          mapped[formKey] = Array.isArray(messages) ? messages[0] : String(messages);
        }
        setFieldErrors(mapped);
        setError('Corregeix els errors del formulari abans de continuar.');
      } else {
        setError(err.message || 'Error inesperat. Torna-ho a intentar.');
      }
      setSubmitting(false);
    }
  };

  const fe = (name) =>
    fieldErrors[name] ? (
      <span className={styles.fieldError}>{fieldErrors[name]}</span>
    ) : null;

  const inputClass = (name) =>
    `${fieldErrors[name] ? styles.inputError : ''}`;

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <section className={styles.section}>
        <h4 className={styles.sectionTitle}>Informació de l'immoble</h4>
        <div className={styles.grid}>
          <label className={styles.field}>
            Nom de l'immoble <span className={styles.required}>*</span>
            <input
              name="propertyName"
              value={form.propertyName}
              onChange={handleChange}
              placeholder="Ex. Apartament Costa Brava"
              className={inputClass('propertyName')}
            />
            {fe('propertyName')}
          </label>

          <label className={styles.field}>
            Referència
            <input
              name="reference"
              value={form.reference}
              onChange={handleChange}
              placeholder="Ex. REF-001"
              className={inputClass('reference')}
            />
            {fe('reference')}
          </label>

          <label className={`${styles.field} ${styles.fullWidth}`}>
            Adreça <span className={styles.required}>*</span>
            <input
              name="address"
              value={form.address}
              onChange={handleChange}
              placeholder="Ex. Carrer Major 12"
              className={inputClass('address')}
            />
            {fe('address')}
          </label>

          <label className={styles.field}>
            Ciutat
            <input
              name="city"
              value={form.city}
              onChange={handleChange}
              placeholder="Ex. Barcelona"
              className={inputClass('city')}
            />
            {fe('city')}
          </label>

          <label className={styles.field}>
            Codi postal
            <input
              name="postalCode"
              value={form.postalCode}
              onChange={handleChange}
              placeholder="Ex. 08001"
              className={inputClass('postalCode')}
            />
            {fe('postalCode')}
          </label>

          <label className={styles.field}>
            Tipus d'immoble
            <input
              name="propertyType"
              value={form.propertyType}
              onChange={handleChange}
              placeholder="Ex. Apartament, Xalet..."
              className={inputClass('propertyType')}
            />
            {fe('propertyType')}
          </label>

          <label className={styles.field}>
            Metres quadrats
            <input
              name="squareMeters"
              type="number"
              min="0"
              value={form.squareMeters}
              onChange={handleChange}
              placeholder="Ex. 80"
              className={inputClass('squareMeters')}
            />
            {fe('squareMeters')}
          </label>

          <label className={styles.field}>
            Capacitat màxima
            <input
              name="capacity"
              type="number"
              min="1"
              value={form.capacity}
              onChange={handleChange}
              placeholder="Ex. 4"
              className={inputClass('capacity')}
            />
            {fe('capacity')}
          </label>

          <label className={styles.field}>
            Habitacions
            <input
              name="bedrooms"
              type="number"
              min="0"
              value={form.bedrooms}
              onChange={handleChange}
              placeholder="Ex. 2"
              className={inputClass('bedrooms')}
            />
            {fe('bedrooms')}
          </label>

          <label className={styles.field}>
            Banys
            <input
              name="bathrooms"
              type="number"
              min="0"
              value={form.bathrooms}
              onChange={handleChange}
              placeholder="Ex. 1"
              className={inputClass('bathrooms')}
            />
            {fe('bathrooms')}
          </label>

          <label className={styles.field}>
            Preu base / nit (€) <span className={styles.required}>*</span>
            <input
              name="basePrice"
              type="number"
              min="0"
              step="0.01"
              value={form.basePrice}
              onChange={handleChange}
              placeholder="Ex. 120"
              className={inputClass('basePrice')}
            />
            {fe('basePrice')}
          </label>
        </div>
      </section>

      <section className={styles.section}>
        <h4 className={styles.sectionTitle}>Informació del propietari</h4>
        <div className={styles.grid}>
          <label className={styles.field}>
            Nom complet
            <input
              name="ownerName"
              value={form.ownerName}
              onChange={handleChange}
              placeholder="Ex. Joan Garcia"
              className={inputClass('ownerName')}
            />
            {fe('ownerName')}
          </label>

          <label className={styles.field}>
            DNI / NIF
            <input
              name="ownerTaxId"
              value={form.ownerTaxId}
              onChange={handleChange}
              placeholder="Ex. 12345678A"
              className={inputClass('ownerTaxId')}
            />
            {fe('ownerTaxId')}
          </label>

          <label className={styles.field}>
            Email
            <input
              name="ownerEmail"
              type="email"
              value={form.ownerEmail}
              onChange={handleChange}
              placeholder="Ex. propietari@email.com"
              className={inputClass('ownerEmail')}
            />
            {fe('ownerEmail')}
          </label>

          <label className={styles.field}>
            Telèfon
            <input
              name="ownerPhone"
              value={form.ownerPhone}
              onChange={handleChange}
              placeholder="Ex. 600 000 000"
              className={inputClass('ownerPhone')}
            />
            {fe('ownerPhone')}
          </label>

          <label className={`${styles.field} ${styles.fullWidth}`}>
            Adreça fiscal
            <input
              name="ownerAddress"
              value={form.ownerAddress}
              onChange={handleChange}
              placeholder="Ex. Carrer Exemple 1, Barcelona"
              className={inputClass('ownerAddress')}
            />
            {fe('ownerAddress')}
          </label>

          <label className={`${styles.field} ${styles.fullWidth}`}>
            IBAN
            <input
              name="ownerIban"
              value={form.ownerIban}
              onChange={handleChange}
              placeholder="Ex. ES12 3456 7890 1234 5678 9012"
              className={inputClass('ownerIban')}
            />
            {fe('ownerIban')}
          </label>
        </div>
      </section>

      {error && (
        <div className={styles.errorBox}>
          <span className={styles.errorIcon}>!</span>
          {error}
        </div>
      )}

      <div className={styles.actions}>
        <button type="button" className={styles.cancelButton} onClick={onCancel}>
          Cancel·lar
        </button>
        <button type="submit" className={styles.submitButton} disabled={submitting}>
          {submitting ? 'Creant...' : 'Crear Immoble'}
        </button>
      </div>
    </form>
  );
}
