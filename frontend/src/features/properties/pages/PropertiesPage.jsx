import { useState } from 'react';
import PropertyForm from '../components/propertyForm';
import styles from './propertiesPage.module.css';

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

  const getStatusClass = (status) => {
    switch (status) {
      case 'Disponible':
        return `${styles.statusBadge} ${styles.statusDisponible}`;
      case 'Reservado':
        return `${styles.statusBadge} ${styles.statusReservado}`;
      case 'Mantenimiento':
        return `${styles.statusBadge} ${styles.statusMantenimiento}`;
      default:
        return styles.statusBadge;
    }
  };

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Inmuebles</h2>
          <p>Gestión inicial de propiedades turísticas</p>
        </div>

        <button
          className={styles.primaryButton}
          onClick={() => setShowForm((prev) => !prev)}
        >
          {showForm ? 'Cerrar formulario' : '+ Nuevo inmueble'}
        </button>
      </div>

      {showForm && (
        <div className={styles.formCard}>
          <div className={styles.formCardHeader}>
            <h3>Nuevo inmueble</h3>
            <p>Completa los datos básicos de la propiedad</p>
          </div>

          <PropertyForm onCreate={handleCreateProperty} />
        </div>
      )}

      <div className={styles.propertiesToolbar}>
        <input
          type="text"
          placeholder="Buscar inmueble..."
          className={styles.searchInput}
        />

        <select className={styles.filterSelect} defaultValue="Todos">
          <option value="Todos">Todos</option>
          <option value="Disponible">Disponible</option>
          <option value="Reservado">Reservado</option>
          <option value="Mantenimiento">Mantenimiento</option>
        </select>
      </div>

      <div className={styles.propertiesGrid}>
        {properties.map((property) => (
          <article className={styles.propertyCard} key={property.id}>
            <div className={styles.propertyCardTop}>
              <div>
                <h3>{property.name}</h3>
                <p>{property.city}</p>
              </div>

              <span className={getStatusClass(property.status)}>
                {property.status}
              </span>
            </div>

            <div className={styles.propertyInfo}>
              <div>
                <span className={styles.propertyLabel}>Dirección</span>
                <strong>{property.address}</strong>
              </div>

              <div>
                <span className={styles.propertyLabel}>Capacidad</span>
                <strong>{property.capacity} huéspedes</strong>
              </div>

              <div>
                <span className={styles.propertyLabel}>Precio</span>
                <strong>{property.price} €/noche</strong>
              </div>
            </div>

            <div className={styles.propertyActions}>
              <button className={styles.secondaryButton}>Ver detalle</button>
              <button className={styles.primaryButton}>Editar</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}