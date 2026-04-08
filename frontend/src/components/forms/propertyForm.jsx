import { useState } from 'react';

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
    <form className="property-form" onSubmit={handleSubmit}>
      <div className="property-form-grid">
        <label>
          Nombre del inmueble
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Ej. Apartamento Costa"
            required
          />
        </label>

        <label>
          Ciudad
          <input
            type="text"
            name="city"
            value={form.city}
            onChange={handleChange}
            placeholder="Ej. Barcelona"
            required
          />
        </label>

        <label className="full-width">
          Dirección
          <input
            type="text"
            name="address"
            value={form.address}
            onChange={handleChange}
            placeholder="Ej. Calle Mayor 12"
            required
          />
        </label>

        <label>
          Capacidad
          <input
            type="number"
            name="capacity"
            value={form.capacity}
            onChange={handleChange}
            placeholder="Ej. 4"
            min="1"
            required
          />
        </label>

        <label>
          Precio por noche
          <input
            type="number"
            name="price"
            value={form.price}
            onChange={handleChange}
            placeholder="Ej. 120"
            min="0"
            required
          />
        </label>

        <label>
          Estado
          <select
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

      <div className="property-form-actions">
        <button type="submit" className="primary-button">
          Guardar inmueble
        </button>
      </div>
    </form>
  );
}