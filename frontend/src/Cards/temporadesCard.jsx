import { propertiesApi } from "../services/api";
import styles from "./temporadesCard.module.css";

export default function TemporadesCard({
  immoble,
  setImmoble,
  onSave: handleDesa,
}) {
  console.log(immoble);

  const handleNovaTemporada = () => {
    const darreraData = immoble.temporades?.reduce(
      (prev, curr, index, array) => {
        const date = new Date(curr.data_fi);

        return date.getTime() > prev.getTime() ? date : prev;
      },
      new Date(0),
    );
    const darreraDataString = `${darreraData.getFullYear()}-${darreraData.getMonth() + 1}-${darreraData.getDate()}`;

    setImmoble((immoble) => ({
      ...immoble,
      temporades: [
        ...(immoble.temporades || []),
        {
          nom: "Nova temporada",
          data_inici: darreraDataString,
          data_fi: darreraDataString,
          preu_nit: 0,
        },
      ],
    }));
  };

  const handleEliminarTemporada = (id) => {
    return () => {
      setImmoble((immoble) => ({
        ...immoble,
        temporades: [...(immoble.temporades || [])].filter(
          (temporada) => temporada.id !== id,
        ),
      }));
    };
  };

  const handleChange = (id, key) => (e) => {
    setImmoble((immoble) => {
      const novesTemporades = [...immoble.temporades].map((temporada) => {
        if (temporada.id === id) {
          temporada[key] = e.target.value;
        }

        return temporada;
      });

      return { ...immoble, temporades: novesTemporades };
    });
  };

  console.log(immoble);

  return (
    <div className={styles.wrapper}>
      <h1>Temporades</h1>

      <div className={""}>
        {immoble.temporades?.map((temporada) => (
          <div className={styles.temporada} key={temporada.id}>
            <input
              type="name"
              defaultValue={temporada.nom}
              onChange={handleChange(temporada.id, "nom")}
            />
            <input
              type="date"
              defaultValue={temporada.data_inici}
              onChange={handleChange(temporada.id, "data_inici")}
            />
            <input
              type="date"
              defaultValue={temporada.data_fi}
              onChange={handleChange(temporada.id, "data_fi")}
            />
            <input
              type="number"
              defaultValue={+temporada.preu_nit}
              onChange={handleChange(temporada.id, "preu_nit")}
            />
            <button onClick={handleEliminarTemporada(temporada.id)}>
              Elimina
            </button>
          </div>
        )) || <>No s'ha trobat cap temporada</>}
        <button onClick={handleNovaTemporada}>Afegeix una temporada</button>
        <button onClick={handleDesa}>Desa</button>
      </div>
    </div>
  );
}
