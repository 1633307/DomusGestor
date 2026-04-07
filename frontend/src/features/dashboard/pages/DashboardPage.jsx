export default function DashboardPage() {
  return (
    <section>
      <h2>Dashboard</h2>
      <div className="grid-cards">
        <article className="card">
          <h3>Resumen</h3>
          <p>Aquí irá el resumen principal del sistema.</p>
        </article>
        <article className="card">
          <h3>Reservas</h3>
          <p>Estado general de reservas y ocupación.</p>
        </article>
        <article className="card">
          <h3>Pagos</h3>
          <p>Más adelante se conectará al backend.</p>
        </article>
      </div>
    </section>
  );
}