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
        <h2>Llistat Inmobles</h2>
      </div>

      <div className={styles.propertiesToolbar}>
        <input
          type="text"
          placeholder="Buscar inmoble"
          className={styles.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading && <p>Carregant...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div className={styles.propertiesGrid}>
        {properties.map((property) => (
          <article className={styles.propertyCard} key={property.id}>
            <Link to={`/infoInmoble/${property.id}`}>
              <h3>{property.nom_comercial}</h3>
              <p>{property.adreca}</p>
              <p>{property.preu_base_nit}€/nit</p>
            </Link>
          </article>
        ))}
        {!loading && properties.length === 0 && <p>No hi ha immobles.</p>}
      </div>
    </section>
  );
}
