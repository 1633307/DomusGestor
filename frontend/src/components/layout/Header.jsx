import { useAuth } from '../../app/authContext';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div>
        <h1>Domus Gestor</h1>
        <p>Gestión de alojamientos turísticos</p>
      </div>

      <div className="header-actions">
        <span>{user?.name || 'Usuario'}</span>
        <button className="secondary-button" onClick={logout}>
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}