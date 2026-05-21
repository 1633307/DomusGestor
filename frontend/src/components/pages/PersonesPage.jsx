import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { personesApi } from "../../services/api";
import styles from "./PersonesPage.module.css";

function comparePersones(a, b) {
  return getPersonaName(a).localeCompare(getPersonaName(b), "ca", {
    sensitivity: "base",
  });
}

function getPersonaName(persona) {
  return persona.nom_complet || persona.fullName || "";
}

function getPersonaDocument(persona) {
  return persona.dni_passaport || persona.documentNumber || "";
}

function getPersonaPhone(persona) {
  return persona.telefon || persona.phone || "";
}

function getPersonaNationality(persona) {
  return persona.nacionalitat || persona.nationality || "";
}

export default function PersonesPage() {
  const navigate = useNavigate();
  const [persones, setPersones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    personesApi
      .list()
      .then((data) => setPersones(data.results ?? data))
      .catch(() => setError("No s'han pogut carregar les persones."))
      .finally(() => setLoading(false));
  }, []);

  const sortedPersones = useMemo(
    () => [...persones].sort(comparePersones),
    [persones],
  );

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <h2>Persones</h2>
        <button
          type="button"
          className={styles.primaryButton}
          onClick={() => navigate("/persones/nova")}
        >
          Afegir persona
        </button>
      </div>

      {loading && <p>Carregant persones...</p>}
      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.personesGrid}>
        {sortedPersones.map((persona) => (
          <article className={styles.personaCard} key={persona.id}>
            <Link to={`/persones/${persona.id}`}>
              <div className={styles.cardHeader}>
                <h3>{getPersonaName(persona) || "Persona sense nom"}</h3>
              </div>

              <div className={styles.personaInfo}>
                <div>
                  <span>Document</span>
                  <strong>{getPersonaDocument(persona) || "-"}</strong>
                </div>
                <div>
                  <span>Correu electrònic</span>
                  <strong>{persona.email || "-"}</strong>
                </div>
                <div>
                  <span>Telèfon</span>
                  <strong>{getPersonaPhone(persona) || "-"}</strong>
                </div>
                <div>
                  <span>Nacionalitat</span>
                  <strong>{getPersonaNationality(persona) || "-"}</strong>
                </div>
              </div>
            </Link>
          </article>
        ))}

        {!loading && !error && sortedPersones.length === 0 && (
          <p>Encara no hi ha persones registrades.</p>
        )}
      </div>
    </section>
  );
}
