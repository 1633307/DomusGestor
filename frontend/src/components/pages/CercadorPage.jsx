import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { propertiesApi } from '../../services/api';
import styles from './cercadorPage.module.css';

export default function CercadorPage() {
  const [properties, setProperties] = useState([]);
  const [search, setSearch] = useState('');
  const [filterActiu, setFilterActiu] = useState('Todos');
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

  const filtered = properties.filter((p) => {
    if (filterActiu === 'Actiu') return p.actiu === true;
    if (filterActiu === 'Inactiu') return p.actiu === false;
    return true;
  });

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Cercador</h2>
        </div>
      </div>

      <div className={styles.propertiesToolbar}>
        <input
          type="text"
          placeholder="Buscar inmueble..."
          className={styles.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          className={styles.filterSelect}
          value={filterActiu}
          onChange={(e) => setFilterActiu(e.target.value)}
        >
          <option value="Todos">Todos</option>
          <option value="Actiu">Activo</option>
          <option value="Inactiu">Inactivo</option>
        </select>
      </div>

      {loading && <p>Carregant...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div className={styles.propertiesGrid}>
        {filtered.map((property) => (
          <article className={styles.propertyCard} key={property.id}>
            <div className={styles.propertyCardTop}>
              <div>
                <h3>{property.nom_comercial}</h3>
                <p>{property.ciutat}</p>
              </div>
            </div>

            <div className={styles.propertyInfo}>
              <div>
                <span className={styles.propertyLabel}>Dirección</span>
                <strong>{property.adreca}</strong>
              </div>

              <div>
                <span className={styles.propertyLabel}>Precio</span>
                <strong>{property.preu_base_nit} €/noche</strong>
              </div>

              {property.foto_principal && (
                <div className={styles.propertyImage}>
                  <img src={property.foto_principal} alt="foto" />
                </div>
              )}
            </div>

            <div className={styles.propertyActions}>
              <Link to={`/infoInmoble/${property.id}`} className={styles.secondaryButton}>
                Ver detalle
              </Link>
            </div>
          </article>
        ))}
        {!loading && filtered.length === 0 && <p>No hi ha immobles.</p>}
      </div>
    </section>
  );
}
