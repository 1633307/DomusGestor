import { useEffect, useState } from 'react';
import PropertyForm from '../components/propertyForm';
import { api } from '../../../services/api';

export default function PropertiesPage() {
  const [properties, setProperties] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('Todos');
  const [loading, setLoading] = useState(true);

  const fetchProperties = async (searchTerm = '') => {
    try {
      const data = await api.getProperties(searchTerm);
      setProperties(data);
    } catch (err) {
      console.error('Error cargando inmuebles:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearch(value);
    fetchProperties(value);
  };

  const handleCreateProperty = async (formData) => {
    try {
      await api.createProperty({
        nom_comercial: formData.name,
        adreca: `${formData.address}, ${formData.city}`,
        preu_base: formData.price,
        capacitat_maxima: formData.capacity,
        actiu: formData.status !== 'Mantenimiento',
      });
      setShowForm(false);
      fetchProperties(search);
    } catch (err) {
      console.error('Error creando inmueble:', err);
    }
  };

  const getStatus = (property) => {
    if (!property.actiu) return 'Mantenimiento';
    const hasReserva = property.reserves_count > 0;
    return hasReserva ? 'Reservado' : 'Disponible';
  };

  const filteredProperties = properties.filter((p) => {
    if (filterStatus === 'Todos') return true;
    return getStatus(p) === filterStatus;
  });

  if (loading) return <p>Cargando...</p>;

  return (
    <section>
      <div className="page-title page-title-row">
        <div>
          <h2>Inmuebles</h2>
          <p>Gestión inicial de propiedades turísticas</p>
        </div>

        <button
          className="primary-button"
          onClick={() => setShowForm((prev) => !prev)}
        >
          {showForm ? 'Cerrar formulario' : '+ Nuevo inmueble'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <div className="form-card-header">
            <h3>Nuevo inmueble</h3>
            <p>Completa los datos básicos de la propiedad</p>
          </div>

          <PropertyForm onCreate={handleCreateProperty} />
        </div>
      )}

      <div className="properties-toolbar">
        <input
          type="text"
          placeholder="Buscar inmueble..."
          className="search-input"
          value={search}
          onChange={handleSearch}
        />

        <select
          className="filter-select"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="Todos">Todos</option>
          <option value="Disponible">Disponible</option>
          <option value="Reservado">Reservado</option>
          <option value="Mantenimiento">Mantenimiento</option>
        </select>
      </div>

      <div className="properties-grid">
        {filteredProperties.map((property) => {
          const status = getStatus(property);
          return (
            <article className="property-card" key={property.id}>
              <div className="property-card-top">
                <div>
                  <h3>{property.nom_comercial}</h3>
                  <p>{property.adreca}</p>
                </div>

                <span
                  className={`status-badge status-${status.toLowerCase()}`}
                >
                  {status}
                </span>
              </div>

              <div className="property-info">
                <div>
                  <span className="property-label">Dirección</span>
                  <strong>{property.adreca}</strong>
                </div>

                <div>
                  <span className="property-label">Capacidad</span>
                  <strong>{property.capacitat_maxima} huéspedes</strong>
                </div>

                <div>
                  <span className="property-label">Precio</span>
                  <strong>{property.preu_base} €/noche</strong>
                </div>
              </div>

              <div className="property-actions">
                <button className="secondary-button">Ver detalle</button>
                <button className="primary-button">Editar</button>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
