import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { propertiesApi } from '../../services/api';
import PropertyForm from '../forms/propertyForm';
import styles from './inmoblesPage.module.css';

export default function InmoblesPage() {
  const [properties, setProperties] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    setLoading(true);
    setError('');
    propertiesApi
      .list(search)
      .then((data) => setProperties(data.results ?? data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [search, refreshKey]);

  const handleCreate = async (payload) => {
    await propertiesApi.create(payload);
    setShowModal(false);
    setRefreshKey((k) => k + 1);
    setSuccessMsg('Immoble creat correctament!');
    setTimeout(() => setSuccessMsg(''), 3500);
  };

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Llistat Immobles</h2>
          <p>Gestiona i consulta tots els immobles registrats</p>
        </div>
        <button className={styles.addButton} onClick={() => setShowModal(true)}>
          + Afegir Immoble
        </button>
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
              className={`${styles.propertyCard} ${property.actiu === false ? styles.propertyCardDisabled : ''}`}
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

      {showModal && (
        <div
          className={styles.modalOverlay}
          onClick={() => setShowModal(false)}
        >
          <div
            className={styles.modalBox}
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.modalHeader}>
              <h3>Afegir Immoble</h3>
              <button
                className={styles.modalClose}
                onClick={() => setShowModal(false)}
                aria-label="Tancar"
              >
                ✕
              </button>
            </div>
            <div className={styles.modalBody}>
              <PropertyForm
                onSubmit={handleCreate}
                onCancel={() => setShowModal(false)}
              />
            </div>
          </div>
        </div>
      )}

      {successMsg && (
        <div className={styles.successToast}>{successMsg}</div>
      )}
    </section>
  );
}
