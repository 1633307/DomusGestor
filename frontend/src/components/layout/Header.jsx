import { useAuth } from '../../features/auth/authContext';
import styles from './Header.module.css';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className={styles.header}>
      <div>
        <h1 className={styles.title}>Domus Gestor</h1>
        <p className={styles.subtitle}>Gestión de alojamientos turísticos</p>
      </div>

      <div className={styles.headerActions}>
        <span>{user?.name || 'Usuario'}</span>
        <button className={styles.secondaryButton} onClick={logout}>
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}