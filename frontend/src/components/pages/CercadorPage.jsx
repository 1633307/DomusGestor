import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { propertiesApi } from '../../services/api';
import styles from './cercadorPage.module.css';
import { DatePickerInput } from '@mantine/dates';
import { Autocomplete } from '@mantine/core';
import { NumberInput } from '@mantine/core';
import { TextInput } from '@mantine/core';
import { Button } from '@mantine/core';
import { useCollapse,useDisclosure } from '@mantine/hooks';
import { IoFilter,IoBed,IoPersonAdd,IoCalendarOutline } from "react-icons/io5";

export default function CercadorPage() {
  const [properties, setProperties] = useState([]);
  const [search, setSearch] = useState('');
  const [filterActiu, setFilterActiu] = useState('Todos');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [properties, setProperties] = useState(initialProperties);
  const [value, setValue] = useState([null,null]);
  const [showfilters, setShowfilters] = useState(false);

  return (
    <section>
      
      <div className={styles.propertiesSerchbar}>
        <div className={styles.propertiesFiltres}>
          <TextInput area="Top"
            label= "Inmoble" />

          <Button area="Top" leftSection={<IoFilter size={14}/>} variant="default" 
          type='button'
          onClick={() => setShowfilters(!showfilters)} >
            {showfilters ? "Tancar" : "Mostrar"} Filtres
          </Button>

          <Button area="Top" className={styles.right}>
          BUSCAR
          </Button>
        </div>
        <div area="Bottom" className={`${styles.Expansion} ${showfilters ? styles.isExpanded : ''}`}>
          <div className={styles.propertiesFiltres}>
       
            <DatePickerInput 
            label={<IoCalendarOutline size={25}/>}
            placeholder='Escull una data'
            type="range"
            value={value}
            onChange={setValue}
            />
            <Autocomplete 
              label="Localització"
              data={['Llafranc','Calella','Tamariu']} 
            
            />
            <NumberInput className={styles.searchNumberInputs}
              label={<IoPersonAdd size={25} />}
            />
            <NumberInput className={styles.searchNumberInputs}
              label={<IoBed size={25} />}
            />
          </div>
        </div>
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
