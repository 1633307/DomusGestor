import styles from './DashboardPage.module.css';

export default function DashboardPage() {
 return (
    <section>
      <div className={styles.pageTitle}>
        <h2>Dashboard</h2>
        <p>Resumen general del sistema</p>
      </div>

      <div className={styles.dashboardGrid}>
        <article className={styles.dashboardCard}>
          <h3>Reservas</h3>
          <p>Aquí irá el resumen de reservas.</p>
        </article>

        <article className={styles.dashboardCard}>
          <h3>Inmobles</h3>
          <p>Aquí irá el resumen de inmuebles.</p>
        </article>

        <article className={styles.dashboardCard}>
          <h3>Clientes</h3>
          <p>Aquí irá el resumen de clientes.</p>
        </article>
      </div>
    </section>
  );
}