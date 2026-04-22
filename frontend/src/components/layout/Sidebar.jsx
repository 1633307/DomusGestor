import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h2>Domus Gestor</h2>
        <p>Panel de gestión</p>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/properties">Inmuebles</NavLink>
      </nav>
    </aside>
  );
}