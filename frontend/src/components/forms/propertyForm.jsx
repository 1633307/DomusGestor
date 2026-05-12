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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await onSubmit(formToBackend(form));
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
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
              required
            />
          </label>

          <label className={styles.field}>
            Referència
            <input
              name="reference"
              value={form.reference}
              onChange={handleChange}
              placeholder="Ex. REF-001"
            />
          </label>

          <label className={`${styles.field} ${styles.fullWidth}`}>
            Adreça <span className={styles.required}>*</span>
            <input
              name="address"
              value={form.address}
              onChange={handleChange}
              placeholder="Ex. Carrer Major 12"
              required
            />
          </label>

          <label className={styles.field}>
            Ciutat
            <input
              name="city"
              value={form.city}
              onChange={handleChange}
              placeholder="Ex. Barcelona"
            />
          </label>

          <label className={styles.field}>
            Codi postal
            <input
              name="postalCode"
              value={form.postalCode}
              onChange={handleChange}
              placeholder="Ex. 08001"
            />
          </label>

          <label className={styles.field}>
            Tipus d'immoble
            <input
              name="propertyType"
              value={form.propertyType}
              onChange={handleChange}
              placeholder="Ex. Apartament, Xalet..."
            />
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
            />
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
            />
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
            />
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
            />
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
              required
            />
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
            />
          </label>

          <label className={styles.field}>
            DNI / NIF
            <input
              name="ownerTaxId"
              value={form.ownerTaxId}
              onChange={handleChange}
              placeholder="Ex. 12345678A"
            />
          </label>

          <label className={styles.field}>
            Email
            <input
              name="ownerEmail"
              type="email"
              value={form.ownerEmail}
              onChange={handleChange}
              placeholder="Ex. propietari@email.com"
            />
          </label>

          <label className={styles.field}>
            Telèfon
            <input
              name="ownerPhone"
              value={form.ownerPhone}
              onChange={handleChange}
              placeholder="Ex. 600 000 000"
            />
          </label>

          <label className={`${styles.field} ${styles.fullWidth}`}>
            Adreça fiscal
            <input
              name="ownerAddress"
              value={form.ownerAddress}
              onChange={handleChange}
              placeholder="Ex. Carrer Exemple 1, Barcelona"
            />
          </label>

          <label className={`${styles.field} ${styles.fullWidth}`}>
            IBAN
            <input
              name="ownerIban"
              value={form.ownerIban}
              onChange={handleChange}
              placeholder="Ex. ES12 3456 7890 1234 5678 9012"
            />
          </label>
        </div>
      </section>

      {error && <p className={styles.errorMsg}>{error}</p>}

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
