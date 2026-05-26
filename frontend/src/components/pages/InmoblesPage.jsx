import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { DatePickerInput } from '@mantine/dates';
import { IoFilter, IoPersonAdd, IoBed } from 'react-icons/io5';
import { api, propertiesApi } from '../../services/api';
import PropertyForm from '../forms/propertyForm';
import styles from './inmoblesPage.module.css';

const formatDate = (date) => {
  if (!date) return null;
  const d = new Date(date);
  const month = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${d.getFullYear()}-${month}-${day}`;
};

export default function InmoblesPage() {
  const [properties, setProperties] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dates, setDates] = useState([null, null]);
  const [city, setCity] = useState('');
  const [guests, setGuests] = useState('');
  const [rooms, setRooms] = useState('');

  useEffect(() => {
    const timer = setTimeout(async () => {
      setIsLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (searchTerm) params.append('search', searchTerm);
        if (city) params.append('ciutat', city);
        if (rooms) params.append('habitacions', rooms);
        if (guests) params.append('capacitat', guests);
        if (dates[0] && dates[1]) {
          params.append('dataini', formatDate(dates[0]));
          params.append('datafi', formatDate(dates[1]));
        }
        const endpoint = `/properties/${params.toString() ? `?${params.toString()}` : ''}`;
        const data = await api.get(endpoint);
        setProperties(data.results ?? data);
      } catch (err) {
        setError(err.message || 'Error al carregar els immobles');
      } finally {
        setIsLoading(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [searchTerm, city, guests, rooms, dates, refreshKey]);

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
          placeholder="Cerca per nom o adreça..."
          className={styles.searchInput}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.currentTarget.value)}
        />
        <button
          className={styles.filterToggleBtn}
          type="button"
          onClick={() => setShowFilters(!showFilters)}
        >
          <IoFilter size={14} />
          {showFilters ? 'Tancar filtres' : 'Filtres'}
        </button>
        {isLoading && <span className={styles.loadingIndicator}>Cercant...</span>}
      </div>

      <div className={`${styles.filterPanel} ${showFilters ? styles.filterPanelOpen : ''}`}>
        <div className={styles.filterGrid}>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>Dates</label>
            <DatePickerInput
              type="range"
              placeholder="Escull un rang de dates"
              value={dates}
              onChange={setDates}
              classNames={{ input: styles.datePickerInput }}
            />
          </div>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>Localització</label>
            <select
              className={styles.filterSelect}
              value={city}
              onChange={(e) => setCity(e.target.value)}
            >
              <option value="">Totes les localitzacions</option>
              <option value="Barcelona">Barcelona</option>
              <option value="Girona">Girona</option>
              <option value="Tarragona">Tarragona</option>
              <option value="Llafranc">Llafranc</option>
              <option value="Calella">Calella</option>
              <option value="Tamariu">Tamariu</option>
            </select>
          </div>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>
              <IoPersonAdd size={14} /> Persones
            </label>
            <input
              type="number"
              className={`${styles.filterSelect} ${styles.filterNumber}`}
              value={guests}
              onChange={(e) => setGuests(e.target.value ? Number(e.target.value) : '')}
              min={1}
              placeholder="—"
            />
          </div>
          <div className={styles.filterItem}>
            <label className={styles.filterLabel}>
              <IoBed size={14} /> Habitacions
            </label>
            <input
              type="number"
              className={`${styles.filterSelect} ${styles.filterNumber}`}
              value={rooms}
              onChange={(e) => setRooms(e.target.value ? Number(e.target.value) : '')}
              min={1}
              placeholder="—"
            />
          </div>
        </div>
      </div>

      {error && <p className={styles.errorMsg}>{error}</p>}

      {isLoading ? (
        <p className={styles.stateMsg}>Carregant immobles...</p>
      ) : (
        <div className={styles.propertiesGrid}>
          {properties.length === 0 && (
            <p className={styles.stateMsg}>No s'han trobat resultats.</p>
          )}
          {properties.map((property) => (
            <Link
              to={`/infoInmoble/${property.id}`}
              key={property.id}
              className={styles.propertyCardLink}
            >
              <article
                className={`${styles.propertyCard} ${property.actiu === false ? styles.propertyCardDisabled : ''}`}
              >
                <div className={styles.cardThumbnail}>
                  <img
                    src={property.fotos?.[0] || `${import.meta.env.BASE_URL}placeHolderCasa.jpg`}
                    alt={property.nom_comercial || 'Immoble'}
                  />
                </div>
                <div className={styles.cardInfo}>
                  <h3>{property.nom_comercial || 'Sense nom'}</h3>
                  <p className={styles.cardSub}>{property.adreca}</p>
                  {property.ciutat && (
                    <p className={styles.cardCity}>{property.ciutat}</p>
                  )}
                </div>
                <div className={styles.cardFooter}>
                  <span className={styles.priceBadge}>{property.preu_base_nit} €/nit</span>
                  <div className={styles.cardMeta}>
                    {property.num_habitacions > 0 && (
                      <span className={styles.metaBadge}>
                        <IoBed size={11} /> {property.num_habitacions} hab.
                      </span>
                    )}
                    {property.capacitat_maxima > 0 && (
                      <span className={styles.metaBadge}>
                        <IoPersonAdd size={11} /> {property.capacitat_maxima} pers.
                      </span>
                    )}
                    {property.actiu === false && (
                      <span className={styles.badgeDisabled}>Deshabilitat</span>
                    )}
                  </div>
                </div>
              </article>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <div className={styles.modalOverlay} onClick={() => setShowModal(false)}>
          <div className={styles.modalBox} onClick={(e) => e.stopPropagation()}>
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
