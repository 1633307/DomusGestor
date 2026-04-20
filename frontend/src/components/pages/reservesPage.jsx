import {useState} from 'react';
import styles from './inmoblesPage.module.css';
import { NavLink } from 'react-router-dom';

const initialReserves = [
  {
      "id": "RES-2026-001",
      "client": {
        "nom": "Marc Rovira",
        "email": "m.rovira@exemple.cat",
        "telefon": "+34 600 112 233"
      },
      "data_entrada": "2026-05-15",
      "data_sortida": "2026-05-20",
      "servei": "Habitació Doble Deluxe",
      "preu_total": 540.50,
      "estat": "confirmada"
    },
    {
      "id": "RES-2026-002",
      "client": {
        "nom": "Laia Font",
        "email": "laia.font@correu.com",
        "telefon": "+34 622 334 455"
      },
      "data_entrada": "2026-06-02",
      "data_sortida": "2026-06-04",
      "servei": "Apartament Loft",
      "preu_total": 210.00,
      "estat": "pendent"
    },
    {
      "id": "RES-2026-003",
      "client": {
        "nom": "Jordi Mestre",
        "email": "jmestre88@servei.net",
        "telefon": "+34 677 889 900"
      },
      "data_entrada": "2026-07-10",
      "data_sortida": "2026-07-17",
      "servei": "Suite Nupcial",
      "preu_total": 1250.00,
      "estat": "pagada"
    },
    {
      "id": "RES-2026-004",
      "client": {
        "nom": "Sílvia Soler",
        "email": "silvia.soler@tinet.cat",
        "telefon": "+34 611 222 333"
      },
      "data_entrada": "2026-08-20",
      "data_sortida": "2026-08-22",
      "servei": "Habitació Individual",
      "preu_total": 145.75,
      "estat": "cancel·lada"
    }
];



export default function reservesPage() {

const [reserves, setReserves] = useState(initialReserves);

return(
 <section>
    <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <h2> Llistat Reserves</h2>
    </div>

    <div className={styles.Toolbar}>
        <input
        type="text"
        placeholder='Buscar inmoble'
        className={styles.searchInput}
        />
    </div>

    <div  className={styles.Grid}>

        {reserves.map((reserva) => (
            <article className={styles.Card} key={reserva.id}>
                <NavLink to="/infoReserva"
                >
                <h3>{reserva.id}</h3></NavLink>
            </article>


        ))}
    </div>

 </section>
);


}