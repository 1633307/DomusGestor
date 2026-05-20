import { useState, useEffect } from 'react';
import { TextInput, Button, Autocomplete, NumberInput } from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import { IoFilter, IoCalendarOutline, IoPersonAdd, IoBed } from 'react-icons/io5';
import { api } from '../../services/api'; // <-- Ruta corregida del paso anterior
import styles from './CercadorPage.module.css';

export default function CercadorPage() {
  // 1. Estados de datos y carga
  const [properties, setProperties] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 2. Estados de los filtros
  const [showfilters, setShowfilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState(''); 
  const [dates, setDates] = useState([null, null]); 
  const [city, setCity] = useState('');
  const [guests, setGuests] = useState(''); // Estado para la capacidad
  const [rooms, setRooms] = useState(''); 

  // 3. Función para formatear la fecha a YYYY-MM-DD para Django
  const formatDate = (date) => {
    if (!date) return null;
    const d = new Date(date);
    const month = `${d.getMonth() + 1}`.padStart(2, '0');
    const day = `${d.getDate()}`.padStart(2, '0');
    const year = d.getFullYear();
    return `${year}-${month}-${day}`;
  };

  // 4. Llamada a la API a través de tu servicio
  const fetchProperties = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      
      if (searchTerm) params.append('search', searchTerm);
      if (city) params.append('ciutat', city);
      if (rooms) params.append('habitacions', rooms);
      
      // 👇 NUEVO CAMBIO: Añadimos el filtro de capacidad al backend 👇
      if (guests) params.append('capacitat', guests);
      
      if (dates[0] && dates[1]) {
        params.append('dataini', formatDate(dates[0]));
        params.append('datafi', formatDate(dates[1]));
      }

      // api.get ya apunta a /api y añade el token automáticamente
      const endpoint = `/properties/${params.toString() ? `?${params.toString()}` : ''}`;
      const data = await api.get(endpoint);
      
      setProperties(data);
      
    } catch (err) {
      setError(err.message || 'Error al cargar los inmuebles');
    } finally {
      setIsLoading(false);
    }
  };

  // Carga inicial al montar el componente
  useEffect(() => {
    fetchProperties();
  }, []);

  const handleSearch = () => {
    fetchProperties();
  };

  return (
    <section>
      <div className={styles.propertiesSerchbar}>
        <div className={styles.propertiesFiltres}>
          <TextInput 
            area="Top"
            label="Inmueble" 
            placeholder="Busca por nombre o dirección..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.currentTarget.value)}
          />

          <Button 
            area="Top" 
            leftSection={<IoFilter size={14}/>} 
            variant="default" 
            type='button'
            onClick={() => setShowfilters(!showfilters)} 
          >
            {showfilters ? "Cerrar" : "Mostrar"} Filtros
          </Button>

          <Button 
            area="Top" 
            className={styles.right}
            onClick={handleSearch}
            loading={isLoading}
          >
            BUSCAR
          </Button>
        </div>

        <div area="Bottom" className={`${styles.Expansion} ${showfilters ? styles.isExpanded : ''}`}>
          <div className={styles.propertiesFiltres}>
            <DatePickerInput 
              label={<IoCalendarOutline size={25}/>}
              placeholder='Escoge una fecha'
              type="range"
              value={dates}
              onChange={setDates}
            />
            <Autocomplete 
              label="Localización"
              placeholder="Ej: Barcelona"
              data={['Barcelona', 'Girona', 'Tarragona', 'Llafranc', 'Calella', 'Tamariu']} 
              value={city}
              onChange={setCity}
            />
            {/* Input de capacidad enlazado al estado guests */}
            <NumberInput 
              className={styles.searchNumberInputs}
              label={<IoPersonAdd size={25} title="Personas" />}
              value={guests}
              onChange={setGuests}
              min={1}
            />
            <NumberInput 
              className={styles.searchNumberInputs}
              label={<IoBed size={25} title="Habitaciones" />}
              value={rooms}
              onChange={setRooms}
              min={1}
            />
          </div>
        </div>
      </div>

      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
      
      {isLoading ? (
        <p style={{ textAlign: 'center' }}>Cargando inmuebles...</p>
      ) : (
        <div className={styles.propertiesGrid}>
          {properties.length === 0 && <p>No se han encontrado resultados.</p>}
          
          {properties.map((property) => (
            <article className={styles.propertyCard} key={property.id}>
              <div className={styles.propertyCardTop}>
                <div>
                  <h3>{property.nom_comercial || 'Sin nombre'}</h3>
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
                
                <div>
                  <span className={styles.propertyLabel}>Habitaciones</span>
                  <strong>{property.num_habitacions}</strong>
                </div>

                {/* Si tienes la capacidad en el modelo del backend, puedes mostrarla aquí también */}
                {property.capacitat && (
                  <div>
                    <span className={styles.propertyLabel}>Capacidad</span>
                    <strong>{property.capacitat} pers.</strong>
                  </div>
                )}

                <div className={styles.propertyImage}>
                  <img src={property.imatge || '/placeHolderCasa.jpg'} alt={property.nom_comercial || 'Inmueble'} />
                </div>
              </div>

              <div className={styles.propertyActions}>
                <button className={styles.secondaryButton}>Ver detalle</button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}