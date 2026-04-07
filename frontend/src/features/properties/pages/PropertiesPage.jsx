import { useState } from 'react';
import PropertyForm from '../components/propertyForm';

const initialProperties = [
  {
    id: 1,
    name: 'Apartamento Costa',
    city: 'Barcelona',
    address: 'Carrer de Mallorca, 120',
    status: 'Disponible',
    capacity: 4,
    price: 120,
  },
  {
    id: 2,
    name: 'Ático Central',
    city: 'Girona',
    address: 'Plaça Catalunya, 8',
    status: 'Reservado',
    capacity: 2,
    price: 95,
  },
  {
    id: 3,
    name: 'Estudio Playa',
    city: 'Tarragona',
    address: 'Passeig Marítim, 22',
    status: 'Mantenimiento',
    capacity: 3,
    price: 80,
  },
  {
    id: 4,
    name: 'Casa Jardín',
    city: 'Sitges',
    address: 'Avinguda del Mar, 14',
    status: 'Disponible',
    capacity: 6,
    price: 180,
  },
];

export default function PropertiesPage() {
  const [properties, setProperties] = useState(initialProperties);
  const [showForm, setShowForm] = useState(false);

  const handleCreateProperty = (newProperty) => {
    setProperties((prev) => [newProperty, ...prev]);
    setShowForm(false);
  };

  return (
    <section>
      <div className="page-title page-title-row">
        <div>
          <h2>Inmuebles</h2>
          <p>Gestión inicial de propiedades turísticas</p>
        </div>

        <button
          className="primary-button"
          onClick={() => setShowForm((prev) => !prev)}
        >
          {showForm ? 'Cerrar formulario' : '+ Nuevo inmueble'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <div className="form-card-header">
            <h3>Nuevo inmueble</h3>
            <p>Completa los datos básicos de la propiedad</p>
          </div>

          <PropertyForm onCreate={handleCreateProperty} />
        </div>
      )}

      <div className="properties-toolbar">
        <input
          type="text"
          placeholder="Buscar inmueble..."
          className="search-input"
        />

        <select className="filter-select" defaultValue="Todos">
          <option value="Todos">Todos</option>
          <option value="Disponible">Disponible</option>
          <option value="Reservado">Reservado</option>
          <option value="Mantenimiento">Mantenimiento</option>
        </select>
      </div>

      <div className="properties-grid">
        {properties.map((property) => (
          <article className="property-card" key={property.id}>
            <div className="property-card-top">
              <div>
                <h3>{property.name}</h3>
                <p>{property.city}</p>
              </div>

              <span
                className={`status-badge status-${property.status.toLowerCase()}`}
              >
                {property.status}
              </span>
            </div>

            <div className="property-info">
              <div>
                <span className="property-label">Dirección</span>
                <strong>{property.address}</strong>
              </div>

              <div>
                <span className="property-label">Capacidad</span>
                <strong>{property.capacity} huéspedes</strong>
              </div>

              <div>
                <span className="property-label">Precio</span>
                <strong>{property.price} €/noche</strong>
              </div>
            </div>

            <div className="property-actions">
              <button className="secondary-button">Ver detalle</button>
              <button className="primary-button">Editar</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}