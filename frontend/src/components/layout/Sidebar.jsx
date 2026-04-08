import { NavLink } from 'react-router-dom';
import styles from './Sidebar.module.css';

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.sidebarBrand}>
        <h2>Domus Gestor</h2>
        <p>Panel de gestión</p>
      </div>

      <nav className={styles.sidebarNav}>
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            isActive
              ? `${styles.link} ${styles.activeLink}`
              : styles.link
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/properties"
          className={({ isActive }) =>
            isActive
              ? `${styles.link} ${styles.activeLink}`
              : styles.link
          }
        >
          Inmuebles
        </NavLink>
      </nav>
    </aside>
  );
}