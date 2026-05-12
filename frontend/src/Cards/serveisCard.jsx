import { useEffect, useState } from "react";
import { serveisApi } from "../services/api";
import styles from "./serveisCard.module.css";

export default function ServeisCard({ immoble, setImmoble, onSave: handleDesa }) {
  const [serveis, setServeis] = useState([]);
  const [hasChanges, setHasChanges] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    serveisApi.list().then((s) => {
      setServeis(
        s.toSorted(({ nom: a }, { nom: b }) => (a < b ? -1 : a > b ? 1 : 0)),
      );
    });
  }, []);

  const handleChange = (id) => (e) => {
    setHasChanges(true);
    setImmoble((prev) => {
      if (e.target.checked) {
        return { ...prev, serveis: [...(prev.serveis || []), id] };
      }
      return { ...prev, serveis: (prev.serveis || []).filter((s) => s !== id) };
    });
  };

  const handleDesar = async () => {
    setSaving(true);
    const ok = await handleDesa();
    setSaving(false);
    if (ok) setHasChanges(false);
  };

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Serveis</h2>
            <p>Selecciona els serveis disponibles a l'immoble</p>
          </div>
        </div>

        {serveis.length ? (
          <div className={styles.serveisGrid}>
            {serveis.map((servei) => (
              <label key={servei.id} className={styles.serveiItem}>
                <input
                  type="checkbox"
                  defaultChecked={immoble.serveis?.includes(servei.id)}
                  onChange={handleChange(servei.id)}
                />
                <span>{servei.nom}</span>
              </label>
            ))}
          </div>
        ) : (
          <p className={styles.emptyState}>Carregant serveis...</p>
        )}

        <div className={styles.actions}>
          <button
            className={hasChanges ? styles.btnPrimary : styles.btnPrimaryClean}
            onClick={handleDesar}
            disabled={saving}
          >
            {saving ? "Desant..." : "Desa"}
          </button>
        </div>
      </section>
    </div>
  );
}
