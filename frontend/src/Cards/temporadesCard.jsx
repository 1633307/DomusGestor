import { useState } from "react";
import styles from "./temporadesCard.module.css";

const MESOS = [
  "Gener", "Febrer", "Març", "Abril", "Maig", "Juny",
  "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre",
];

function SelectMesDia({ value, onChange }) {
  const pad = (n) => String(n).padStart(2, "0");
  const parts = value ? value.split("-") : [];
  const mes = parseInt(parts[1], 10) || 1;
  const dia = parseInt(parts[2], 10) || 1;

  const emit = (nouMes, nouDia) =>
    onChange({ target: { value: `2000-${pad(nouMes)}-${pad(nouDia)}` } });

  return (
    <div className={styles.mesDia}>
      <select
        className={styles.select}
        value={mes}
        onChange={(e) => emit(e.target.value, dia)}
      >
        {MESOS.map((nom, i) => (
          <option key={i + 1} value={i + 1}>{nom}</option>
        ))}
      </select>
      <select
        className={styles.select}
        value={dia}
        onChange={(e) => emit(mes, e.target.value)}
      >
        {Array.from({ length: 31 }, (_, i) => i + 1).map((d) => (
          <option key={d} value={d}>{d}</option>
        ))}
      </select>
    </div>
  );
}

const DIES = [
  [0, "Dl"], [1, "Dt"], [2, "Dc"], [3, "Dj"], [4, "Dv"], [5, "Ds"], [6, "Dg"],
];

function detectaSolapament(temporades) {
  const sorted = [...temporades].sort(
    (a, b) => new Date(a.data_inici) - new Date(b.data_inici)
  );
  for (let i = 0; i < sorted.length - 1; i++) {
    const a = sorted[i];
    const b = sorted[i + 1];
    if (new Date(a.data_fi) >= new Date(b.data_inici)) {
      return `"${a.nom}" i "${b.nom}"`;
    }
  }
  return null;
}

export default function TemporadesCard({ immoble, setImmoble, onSave: handleDesa }) {
  const [errorSolapament, setErrorSolapament] = useState(null);
  const handleNovaTemporada = () => {
    const darreraData = immoble.temporades?.reduce(
      (prev, curr) => {
        const date = new Date(curr.data_fi);
        return date.getTime() > prev.getTime() ? date : prev;
      },
      new Date("2000-01-01"),
    );
    const pad = (n) => String(n).padStart(2, "0");
    const darreraDataString = `2000-${pad(darreraData.getMonth() + 1)}-${pad(darreraData.getDate())}`;

    setImmoble((prev) => ({
      ...prev,
      temporades: [
        ...(prev.temporades || []),
        { nom: "Nova temporada", data_inici: darreraDataString, data_fi: darreraDataString, preu_nit: 0, min_nits: 1, dies_checkin: [] },
      ],
    }));
  };

  const handleEliminarTemporada = (id) => () => {
    setErrorSolapament(null);
    setImmoble((prev) => ({
      ...prev,
      temporades: (prev.temporades || []).filter((t) => t.id !== id),
    }));
  };

  const handleChange = (id, key) => (e) => {
    setErrorSolapament(null);
    const value = key === "min_nits" ? Number(e.target.value) : e.target.value;
    setImmoble((prev) => ({
      ...prev,
      temporades: prev.temporades.map((t) =>
        t.id === id ? { ...t, [key]: value } : t
      ),
    }));
  };

  const handleCheckinChange = (id, dia) => {
    setImmoble((prev) => ({
      ...prev,
      temporades: prev.temporades.map((t) => {
        if (t.id !== id) return t;
        const current = t.dies_checkin || [];
        const updated = current.includes(dia)
          ? current.filter((d) => d !== dia)
          : [...current, dia].sort((a, b) => a - b);
        return { ...t, dies_checkin: updated };
      }),
    }));
  };

  const handleDesar = () => {
    const solapament = detectaSolapament(immoble.temporades || []);
    if (solapament) {
      setErrorSolapament(`Les temporades ${solapament} es solapen. Corregeix els períodes abans de desar.`);
      return;
    }
    setErrorSolapament(null);
    handleDesa();
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
                    <SelectMesDia
                      value={temporada.data_inici}
                      onChange={handleChange(temporada.id, "data_inici")}
                    />
                  </div>
                  <div className={styles.field}>
                    <label>Data fi</label>
                    <SelectMesDia
                      value={temporada.data_fi}
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
                  <div className={styles.field}>
                    <label>Mínim nits</label>
                    <input
                      type="number"
                      min="1"
                      defaultValue={temporada.min_nits ?? 1}
                      onChange={handleChange(temporada.id, "min_nits")}
                    />
                  </div>
                  <div className={`${styles.field} ${styles.fieldFull}`}>
                    <label>
                      Dies de check-in permesos
                      {!(temporada.dies_checkin?.length) && (
                        <span className={styles.anyDay}> · Qualsevol dia</span>
                      )}
                    </label>
                    <div className={styles.checksGroup}>
                      {DIES.map(([val, label]) => (
                        <label key={val} className={styles.checkItem}>
                          <input
                            type="checkbox"
                            checked={(temporada.dies_checkin || []).includes(val)}
                            onChange={() => handleCheckinChange(temporada.id, val)}
                          />
                          {label}
                        </label>
                      ))}
                    </div>
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

        {errorSolapament && (
          <p className={styles.errorSolapament}>{errorSolapament}</p>
        )}

        <div className={styles.actions}>
          <button className={styles.btnSecondary} onClick={handleNovaTemporada}>
            + Afegeix temporada
          </button>
          <button className={styles.btnPrimary} onClick={handleDesar}>
            Desa
          </button>
        </div>
      </section>
    </div>
  );
}
