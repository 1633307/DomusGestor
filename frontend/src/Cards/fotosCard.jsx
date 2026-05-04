import { useState, useEffect } from 'react';
import styles from './fotosCard.module.css';

export default function FotosCard({ fotos = [] }) {
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape') setSelected(null);
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Galeria de fotos</h2>
            <p>{fotos.length} {fotos.length === 1 ? 'foto' : 'fotos'}</p>
          </div>
        </div>

        {fotos.length === 0 ? (
          <div className={styles.empty}>
            <span className={styles.emptyIcon}>🖼️</span>
            <p>Aquest immoble no té fotos assignades</p>
          </div>
        ) : (
          <div className={styles.grid}>
            {fotos.map((url, i) => (
              <button
                key={i}
                className={styles.thumb}
                onClick={() => setSelected(i)}
                aria-label={`Veure foto ${i + 1}`}
              >
                <img src={url} alt={`Foto ${i + 1}`} />
                {i === 0 && <span className={styles.portadaBadge}>Portada</span>}
              </button>
            ))}
          </div>
        )}
      </div>

      {selected !== null && (
        <div
          className={styles.overlay}
          onClick={() => setSelected(null)}
          role="dialog"
          aria-modal="true"
        >
          <button
            className={styles.closeBtn}
            onClick={() => setSelected(null)}
            aria-label="Tancar"
          >
            ✕
          </button>
          <img
            src={fotos[selected]}
            alt={`Foto ${selected + 1}`}
            className={styles.fullImg}
            onClick={(e) => e.stopPropagation()}
          />
          <p className={styles.counter}>{selected + 1} / {fotos.length}</p>
        </div>
      )}
    </div>
  );
}
