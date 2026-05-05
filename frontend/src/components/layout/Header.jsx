import { useAuth } from '../../app/authContext';
import { NavLink } from 'react-router-dom';
import styles from './Header.module.css';
export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className={styles.header}>
      <div class="col1">
        <h1 className={styles.title}>Domus Gestor</h1>
        
      </div>

      <div class="col2" className={styles.headerActions}>
        <span>{user?.name || 'Usuario'}</span>
        <button className={styles.secondaryButton} onClick={logout}>
          Cerrar sesión
        </button>
      </div>

      <div class="fila">
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
                Cercador
              </NavLink>
      
              <NavLink
              to="/inmobles"
                className={({ isActive }) =>
                  isActive
                    ? `${styles.link} ${styles.activeLink}`
                    : styles.link
                }
              >
                Inmobles
              </NavLink>
              <NavLink
              to="/reserves"
                className={({ isActive }) =>
                  isActive
                    ? `${styles.link} ${styles.activeLink}`
                    : styles.link
                }
              >
                Reserves
              </NavLink>
        </nav>
      
      </div>

      
    </header>
  );
}