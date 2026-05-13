import { useAuth } from '../../app/authContext';
import { Link, NavLink } from 'react-router-dom';
import styles from './Header.module.css';

export default function Header() {
  const { user, logout } = useAuth();
  const displayName = user?.name || user?.username || user?.email || 'Usuari';
  const initial = displayName.charAt(0).toUpperCase();

  return (
    <header className={styles.header}>
      <div className={styles.col1}>
        <h1 className={styles.title}>Domus Gestor</h1>
      </div>

      <div className={styles.headerActions}>
        <Link
          to="/perfil-immobiliaria"
          className={styles.userLink}
          title="Perfil de la immobiliària"
        >
          <span className={styles.avatar}>{initial}</span>
          <span>{displayName}</span>
        </Link>
        <button className={styles.secondaryButton} onClick={logout}>
          Tancar sessió
        </button>
      </div>

      <div className={styles.fila}>
        <nav className={styles.sidebarNav}>
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/properties"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Cercador
          </NavLink>

          <NavLink
            to="/inmobles"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Inmobles
          </NavLink>

          <NavLink
            to="/reserves"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Reserves
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
