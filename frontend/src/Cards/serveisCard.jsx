import { useEffect, useState } from "react";
import { propertiesApi, serveisApi } from "../services/api";
import styles from "./serveisCard.module.css";

export default function ServeisCard({
  immoble,
  setImmoble,
  onSave: handleDesa,
}) {
  const [serveis, setServeis] = useState([]);

  useEffect(() => {
    serveisApi.list().then((s) => {
      setServeis(
        s.toSorted(({ nom: a }, { nom: b }) => (a < b ? -1 : a > b ? 1 : 0)),
      );
    });
  }, []);

  const handleChange = (id) => {
    return (e) => {
      setImmoble((immoble) => {
        if (e.target.checked) {
          return { ...immoble, serveis: [...(immoble.serveis || []), id] };
        } else {
          return {
            ...immoble,
            serveis: (immoble.serveis || []).filter((servei) => servei !== id),
          };
        }
      });
    };
  };

  return (
    <div className={styles.wrapper}>
      <h1>Serveis</h1>

      <div>
        {serveis.length
          ? serveis.map((servei) => (
              <div>
                <input
                  type="checkbox"
                  name={servei.id}
                  id=""
                  defaultChecked={immoble.serveis?.includes(servei.id)}
                  onChange={handleChange(servei.id)}
                />
                <span>{servei.nom}</span>
              </div>
            ))
          : "Carregant..."}
        <button onClick={handleDesa}>Desa</button>
      </div>
    </div>
  );
}
