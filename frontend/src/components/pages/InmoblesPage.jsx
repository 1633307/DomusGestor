import {useState} from 'react';
import styles from './inmoblesPage.module.css';
import { NavLink } from 'react-router-dom';

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



export default function InmoblesPage() {

const [properties, setProperties] = useState(initialProperties);

return(
 <section>
    <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <h2> Llistat Inmobles</h2>
    </div>

    <div className={styles.propertiesToolbar}>
        <input
        type="text"
        placeholder='Buscar inmoble'
        className={styles.searchInput}
        />
    </div>

    <div  className={styles.propertiesGrid}>

        {properties.map((property) => (
            <article className={styles.propertyCard} key={property.id}>
                <NavLink to="/infoInmoble">
                <h3>{property.name}</h3></NavLink>
            </article>


        ))}
    </div>

 </section>
);


} 