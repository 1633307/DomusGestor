import { useAuth } from '../../features/auth/authContext';

export default function Header() {
  const { logout, user } = useAuth();

  return (
    <header className="header">
      <div>
        <h1>Domus Gestor</h1>
        <p>Panel de gestión</p>
      </div>

      <div className="header-actions">
        <span>{user?.name || 'Usuario'}</span>
        <button className="btn btn-secondary" onClick={logout}>
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}