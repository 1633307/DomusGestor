import { useState } from "react";
import styles from "./Sidebar.module.css";

export default function Sidebar({
  setSeccioActiva,
  seccioActiva,
  seccions = [],
  actiu,
  onDeshabilitar,
  onEliminar,
}) {
  const [modalDeshabilitar, setModalDeshabilitar] = useState(false);
  const [modalEliminar, setModalEliminar] = useState(false);

  const sidebarClass = actiu === false
    ? `${styles.sidebar} ${styles.sidebarDisabled}`
    : styles.sidebar;

  return (
    <>
      <aside className={sidebarClass}>
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

        {(onDeshabilitar || onEliminar) && (
          <div className={styles.sidebarActions}>
            {actiu !== false ? (
              <button
                className={styles.btnDeshabilitar}
                onClick={() => setModalDeshabilitar(true)}
              >
                Deshabilitar
              </button>
            ) : (
              <button
                className={styles.btnEliminar}
                onClick={() => setModalEliminar(true)}
              >
                Eliminar
              </button>
            )}
          </div>
        )}
      </aside>

      {modalDeshabilitar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Deshabilitar immoble</h3>
            <p>Estàs segur que vols deshabilitar aquest immoble? L'immoble deixarà d'estar actiu.</p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalDeshabilitar(false)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmDeshabilitar}
                onClick={() => {
                  setModalDeshabilitar(false);
                  onDeshabilitar?.();
                }}
              >
                Deshabilitar
              </button>
            </div>
          </div>
        </div>
      )}

      {modalEliminar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Eliminar immoble</h3>
            <p>Estàs segur que vols eliminar aquest immoble? Aquesta acció és irreversible i s'eliminaran totes les dades associades.</p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalEliminar(false)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmEliminar}
                onClick={() => {
                  setModalEliminar(false);
                  onEliminar?.();
                }}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
