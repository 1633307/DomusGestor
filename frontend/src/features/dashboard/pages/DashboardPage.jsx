export default function DashboardPage() {
  return (
    <section>
      <div className="page-title">
        <h2>Dashboard</h2>
        <p>Resumen general del sistema</p>
      </div>

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <h3>Reservas</h3>
          <p>Aquí irá el resumen de reservas.</p>
        </article>

        <article className="dashboard-card">
          <h3>Inmuebles</h3>
          <p>Aquí irá el resumen de inmuebles.</p>
        </article>

        <article className="dashboard-card">
          <h3>Clientes</h3>
          <p>Aquí irá el resumen de clientes.</p>
        </article>
      </div>
    </section>
  );
}