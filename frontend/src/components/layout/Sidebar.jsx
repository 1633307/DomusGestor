import { NavLink } from 'react-router-dom';
import styles from './Sidebar.module.css';

export default function Sidebar({setSeccioActiva, seccioActiva}) {

  const menuItems = [
    {id: 'perfil',label:'Perfil'},
    {id: 'descompte', label: 'Descompte'},
    {id: 'novaReserva', label: 'Nova reserva'},
    {id: 'fotos',label:'Fotos'},
    {id: 'incidencies', label: 'Incidéncies'},
    {id: 'info', label:'Informació'},
    {id:'hospedes', label:'Hospedes'},
    {id:'pagaments', label:'Pagaments'},
    {id: 'comunicacions', label: 'Comunicacions'}
  ];


  return (
    <aside className={styles.sidebar}>

      <nav className={styles.sidebarNav}>
        {menuItems.map((item) => (
          <div
            key={item.id}
            onClick={() => setSeccioActiva(item.id)}
            className={`${styles.link} ${seccioActiva === item.id ? styles.activeLink : ''}`}
          >
            {item.label}
          </div>
        ))}
      </nav>
    </aside>
  );
}
