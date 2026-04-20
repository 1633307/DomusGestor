import { NavLink } from 'react-router-dom';
import styles from './Sidebar.module.css';

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>

      <nav className={styles.sidebarNav}>
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            isActive
              ? `${styles.link} ${styles.activeLink}`
              : styles.link
          }
        >
          Perfil
        </NavLink>

        <NavLink
          to="/properties"
          className={({ isActive }) =>
            isActive
              ? `${styles.link} ${styles.activeLink}`
              : styles.link
          }
        >
          Fotos
        </NavLink>

        <NavLink
        to="/inmobles"
          className={({ isActive }) =>
            isActive
              ? `${styles.link} ${styles.activeLink}`
              : styles.link
          }
        >
          Incidències
        </NavLink>
      </nav>
    </aside>
  );
}