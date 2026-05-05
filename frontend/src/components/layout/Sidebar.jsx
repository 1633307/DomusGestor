import { NavLink } from "react-router-dom";
import styles from "./Sidebar.module.css";

export default function Sidebar({ setSeccioActiva, seccioActiva, seccions }) {
  return (
    <aside className={styles.sidebar}>
      <nav className={styles.sidebarNav}>
        {seccions.map((item) => (
          <div
            key={item.id}
            onClick={() => setSeccioActiva(item.id)}
            className={`${styles.link} ${seccioActiva === item.id ? styles.activeLink : ""}`}
          >
            {item.label}
          </div>
        ))}
      </nav>
    </aside>
  );
}
