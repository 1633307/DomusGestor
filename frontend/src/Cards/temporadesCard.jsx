import styles from "./temporadesCard.module.css";

export default function TemporadesCard({ immoble, setImmoble, onSave: handleDesa }) {
  const handleNovaTemporada = () => {
    const darreraData = immoble.temporades?.reduce(
      (prev, curr) => {
        const date = new Date(curr.data_fi);
        return date.getTime() > prev.getTime() ? date : prev;
      },
      new Date(0),
    );
    const pad = (n) => String(n).padStart(2, "0");
    const darreraDataString = `${darreraData.getFullYear()}-${pad(darreraData.getMonth() + 1)}-${pad(darreraData.getDate())}`;

    setImmoble((prev) => ({
      ...prev,
      temporades: [
        ...(prev.temporades || []),
        { nom: "Nova temporada", data_inici: darreraDataString, data_fi: darreraDataString, preu_nit: 0 },
      ],
    }));
  };

  const handleEliminarTemporada = (id) => () => {
    setImmoble((prev) => ({
      ...prev,
      temporades: (prev.temporades || []).filter((t) => t.id !== id),
    }));
  };

  const handleChange = (id, key) => (e) => {
    setImmoble((prev) => ({
      ...prev,
      temporades: prev.temporades.map((t) =>
        t.id === id ? { ...t, [key]: e.target.value } : t
      ),
    }));
  };

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Temporades</h2>
            <p>Configura els períodes de preus de l'immoble</p>
          </div>
        </div>

        {immoble.temporades?.length ? (
          <div className={styles.temporadesList}>
            {immoble.temporades.map((temporada, i) => (
              <div className={styles.temporadaRow} key={temporada.id ?? i}>
                <div className={styles.temporadaGrid}>
                  <div className={styles.field}>
                    <label>Nom</label>
                    <input
                      type="text"
                      defaultValue={temporada.nom}
                      onChange={handleChange(temporada.id, "nom")}
                    />
                  </div>
                  <div className={styles.field}>
                    <label>Data inici</label>
                    <input
                      type="date"
                      defaultValue={temporada.data_inici}
                      onChange={handleChange(temporada.id, "data_inici")}
                    />
                  </div>
                  <div className={styles.field}>
                    <label>Data fi</label>
                    <input
                      type="date"
                      defaultValue={temporada.data_fi}
                      onChange={handleChange(temporada.id, "data_fi")}
                    />
                  </div>
                  <div className={styles.field}>
                    <label>Preu/nit (€)</label>
                    <input
                      type="number"
                      defaultValue={+temporada.preu_nit}
                      onChange={handleChange(temporada.id, "preu_nit")}
                    />
                  </div>
                </div>
                <button
                  className={styles.btnDanger}
                  onClick={handleEliminarTemporada(temporada.id)}
                >
                  Elimina
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className={styles.emptyState}>No s'ha trobat cap temporada</p>
        )}

        <div className={styles.actions}>
          <button className={styles.btnSecondary} onClick={handleNovaTemporada}>
            + Afegeix temporada
          </button>
          <button className={styles.btnPrimary} onClick={handleDesa}>
            Desa
          </button>
        </div>
      </section>
    </div>
  );
}
