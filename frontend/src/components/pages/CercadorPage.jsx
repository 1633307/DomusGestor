import { useState } from 'react';
import PropertyForm from '../forms/propertyForm';
import styles from './cercadorPage.module.css';


const initialProperties = [
  {
    id: 1,
    name: 'Apartamento Costa',
    city: 'Barcelona',
    address: 'Carrer de Mallorca, 120',
    status: 'Disponible',
    capacity: 4,
    price: 120,
    image: '/placeHolderCasa.jpg',
  },
  {
    id: 2,
    name: 'Ático Central',
    city: 'Girona',
    address: 'Plaça Catalunya, 8',
    status: 'Reservado',
    capacity: 2,
    price: 95,
    image: '/placeHolderCasa.jpg',
  },
  {
    id: 3,
    name: 'Estudio Playa',
    city: 'Tarragona',
    address: 'Passeig Marítim, 22',
    status: 'Mantenimiento',
    capacity: 3,
    price: 80,
    image: '/placeHolderCasa.jpg',
  },
  {
    id: 4,
    name: 'Casa Jardín',
    city: 'Sitges',
    address: 'Avinguda del Mar, 14',
    status: 'Disponible',
    capacity: 6,
    price: 180,
    image: '/placeHolderCasa.jpg',
  },
];

export default function CercadorPage() {
  const [properties, setProperties] = useState(initialProperties);



  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Cercador</h2>
        </div>
      </div>

      

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

              
            </div>

            <div className={styles.propertyInfo}>
              <div>
                <span className={styles.propertyLabel}>Dirección</span>
                <strong>{property.address}</strong>
              </div>

              <div>
                <span className={styles.propertyLabel}>Precio</span>
                <strong>{property.price} €/noche</strong>
              </div>

              <div className={styles.propertyImage}>
              <img src={property.image} alt="foto"></img>
              </div>
            </div>

            

            <div className={styles.propertyActions}>
              <button className={styles.secondaryButton}>Ver detalle</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}