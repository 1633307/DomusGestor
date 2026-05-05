import { useState } from 'react';
import styles from './PropertyForm.module.css';
const initialForm = {
  name: '',
  city: '',
  address: '',
  capacity: '',
  price: '',
  status: 'Disponible',
};

export default function PropertyForm({ onCreate }) {
  const [form, setForm] = useState(initialForm);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const newProperty = {
      id: Date.now(),
      name: form.name,
      city: form.city,
      address: form.address,
      capacity: Number(form.capacity),
      price: Number(form.price),
      status: form.status,
    };

    onCreate(newProperty);
    setForm(initialForm);
  };

  return (
    <form className={styles.propertyForm} onSubmit={handleSubmit}>
      <div className={styles.propertyFormGrid}>
        <label className={styles.field}>
          Nombre del inmueble
          <input
            className={styles.input}
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Ej. Apartamento Costa"
            required
          />
        </label>

        <label className={styles.field}>
          Ciudad
          <input
            className={styles.input}
            type="text"
            name="city"
            value={form.city}
            onChange={handleChange}
            placeholder="Ej. Barcelona"
            required
          />
        </label>

        <label className={`${styles.field} ${styles.fullWidth}`}>
          Dirección
          <input
            className={styles.input}
            type="text"
            name="address"
            value={form.address}
            onChange={handleChange}
            placeholder="Ej. Calle Mayor 12"
            required
          />
        </label>

        <label className={styles.field}>
          Capacidad
          <input
            className={styles.input}
            type="number"
            name="capacity"
            value={form.capacity}
            onChange={handleChange}
            placeholder="Ej. 4"
            min="1"
            required
          />
        </label>

        <label className={styles.field}>
          Precio por noche
          <input
            className={styles.input}
            type="number"
            name="price"
            value={form.price}
            onChange={handleChange}
            placeholder="Ej. 120"
            min="0"
            required
          />
        </label>

        <label className={styles.field}>
          Estado
          <select
            className={styles.select}
            name="status"
            value={form.status}
            onChange={handleChange}
          >
            <option value="Disponible">Disponible</option>
            <option value="Reservado">Reservado</option>
            <option value="Mantenimiento">Mantenimiento</option>
          </select>
        </label>
      </div>

      <div className={styles.propertyFormActions}>
        <button type="submit" className={styles.primaryButton}>
          Guardar inmueble
        </button>
      </div>
    </form>
  );
}