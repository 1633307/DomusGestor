import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { personesApi } from '../../services/api';
import styles from './PersonesPage.module.css';

export default function PersonesPage() {
  const navigate = useNavigate();
  const [persones, setPersones] = useState([]);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    personesApi
      .list()
      .then((data) => setPersones(data.results ?? data))
      .catch(() => setError("No s'han pogut carregar les persones."))
      .finally(() => setLoading(false));
  }, []);

  const filteredPersones = useMemo(() => {
    const q = search.toLowerCase();
    return [...persones]
      .filter((persona) => {
        if (roleFilter === 'inquili') {
          return persona.perfil_inquili !== null && persona.perfil_inquili !== undefined;
        }
        if (roleFilter === 'propietari') {
          return persona.perfil_propietari !== null && persona.perfil_propietari !== undefined;
        }
        return true;
      })
      .filter((persona) => {
        if (!q) return true;
        return (
          (persona.nom_complet || '').toLowerCase().includes(q) ||
          (persona.dni_passaport || '').toLowerCase().includes(q) ||
          (persona.email || '').toLowerCase().includes(q)
        );
      })
      .sort((a, b) =>
        (a.nom_complet || '').localeCompare(b.nom_complet || '', 'ca', { sensitivity: 'base' })
      );
  }, [persones, search, roleFilter]);

  return (
    <section>
      <div className={`${styles.pageTitle} ${styles.pageTitleRow}`}>
        <div>
          <h2>Llistat Persones</h2>
          <p>Gestiona i consulta totes les persones registrades</p>
        </div>
        <button className={styles.addButton} onClick={() => navigate('/persones/nova')}>
          + Afegir persona
        </button>
      </div>

      <div className={styles.personesToolbar}>
        <input
          type="text"
          placeholder="Cercar per nom, document o email..."
          className={styles.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className={styles.roleFilters}>
          <button
            className={`${styles.roleFilter} ${roleFilter === 'all' ? styles.roleFilterActive : ''}`}
            onClick={() => setRoleFilter('all')}
          >
            Tots
          </button>
          <button
            className={`${styles.roleFilter} ${roleFilter === 'inquili' ? styles.roleFilterActive : ''}`}
            onClick={() => setRoleFilter('inquili')}
          >
            Hostes
          </button>
          <button
            className={`${styles.roleFilter} ${roleFilter === 'propietari' ? styles.roleFilterActive : ''}`}
            onClick={() => setRoleFilter('propietari')}
          >
            Propietaris
          </button>
        </div>
      </div>

      {loading && <p className={styles.stateMsg}>Carregant...</p>}
      {error && <p className={styles.errorMsg}>{error}</p>}

      <div className={styles.personesGrid}>
        {filteredPersones.map((persona) => (
          <Link to={`/persones/${persona.id}`} key={persona.id} className={styles.personaCardLink}>
            <article className={styles.personaCard}>
              <div className={styles.cardInfo}>
                <h3>{persona.nom_complet || 'Persona sense nom'}</h3>
                <p className={styles.cardSub}>
                  {[persona.dni_passaport, persona.email, persona.telefon]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
              </div>
              <div className={styles.cardFooter}>
                {persona.perfil_inquili && (
                  <span className={styles.badgeInquili}>Hoste</span>
                )}
                {persona.perfil_propietari && (
                  <span className={styles.badgePropietari}>Propietari</span>
                )}
              </div>
            </article>
          </Link>
        ))}
        {!loading && !error && filteredPersones.length === 0 && (
          <p className={styles.stateMsg}>No hi ha persones registrades.</p>
        )}
      </div>
    </section>
  );
}
