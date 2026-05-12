import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { propertiesApi } from '../../services/api';
import styles from './inmoblesPage.module.css';

export default function InmoblesPage() {
  const [properties, setProperties] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    propertiesApi
      .list(search)
      .then((data) => setProperties(data.results ?? data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [search]);

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Llistat Immobles</h2>
          <p>Gestiona i consulta tots els immobles registrats</p>
        </div>
      </div>

      <div className={styles.propertiesToolbar}>
        <input
          type="text"
          placeholder="Cercar immobles..."
          className={styles.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading && <p className={styles.stateMsg}>Carregant...</p>}
      {error && <p className={styles.errorMsg}>{error}</p>}

      <div className={styles.propertiesGrid}>
        {properties.map((property) => (
          <Link
            to={`/infoInmoble/${property.id}`}
            key={property.id}
            className={styles.propertyCardLink}
          >
            <article
              className={`${styles.propertyCard} ${property.actiu === false ? styles.propertyCardDisabled : ""}`}
            >
              <div className={styles.cardInfo}>
                <h3>{property.nom_comercial}</h3>
                <p className={styles.cardAddress}>{property.adreca}</p>
              </div>
              <div className={styles.cardFooter}>
                <span className={styles.priceBadge}>{property.preu_base_nit}€/nit</span>
                {property.actiu === false && (
                  <span className={styles.badgeDisabled}>Deshabilitat</span>
                )}
              </div>
            </article>
          </Link>
        ))}
        {!loading && properties.length === 0 && (
          <p className={styles.stateMsg}>No hi ha immobles.</p>
        )}
      </div>
    </section>
  );
}
