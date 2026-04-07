const mockProperties = [
  {
    id: 1,
    name: 'Apartamento Costa',
    city: 'Barcelona',
    status: 'Disponible',
  },
  {
    id: 2,
    name: 'Ático Central',
    city: 'Girona',
    status: 'Reservado',
  },
  {
    id: 3,
    name: 'Estudio Playa',
    city: 'Tarragona',
    status: 'Mantenimiento',
  },
];

export default function PropertiesPage() {
  return (
    <section>
      <div className="page-title page-title-row">
        <div>
          <h2>Inmuebles</h2>
          <p>Listado inicial de propiedades</p>
        </div>

        <button className="primary-button">+ Nuevo inmueble</button>
      </div>

      <div className="dashboard-grid">
        {mockProperties.map((property) => (
          <article className="dashboard-card" key={property.id}>
            <h3>{property.name}</h3>
            <p>{property.city}</p>
            <span className="status-badge">{property.status}</span>
          </article>
        ))}
      </div>
    </section>
  );
}