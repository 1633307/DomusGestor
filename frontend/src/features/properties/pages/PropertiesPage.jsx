const mockProperties = [
  {
    id: 1,
    name: 'Apartamento Costa Brava',
    city: 'Lloret de Mar',
    status: 'Disponible',
  },
  {
    id: 2,
    name: 'Ático Centro',
    city: 'Barcelona',
    status: 'Reservado',
  },
];

export default function PropertiesPage() {
  return (
    <section>
      <div className="page-title-row">
        <div>
          <h2>Inmuebles</h2>
          <p>Catálogo inicial de propiedades</p>
        </div>

        <button className="btn">+ Nuevo inmueble</button>
      </div>

      <div className="grid-cards">
        {mockProperties.map((property) => (
          <article className="card" key={property.id}>
            <h3>{property.name}</h3>
            <p>{property.city}</p>
            <span className="badge">{property.status}</span>
          </article>
        ))}
      </div>
    </section>
  );
}