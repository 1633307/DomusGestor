import LoginForm from '../components/LoginForm';
import styles from './loginPage.module.css';

export default function LoginPage() {
  return (
    <section className={styles.loginPage}>
      <div className={styles.loginBox}>
        <div className={styles.loginHeader}>
          <p className={styles.loginTag}>Domus Gestor</p>
          <h1 className={styles.title}>Iniciar sesión</h1>
          <p className={styles.loginSubtitle}>
            Accede a la plataforma de gestión de alojamientos turísticos,
            reservas, propietarios e inquilinos.
          </p>
        </div>

        <LoginForm />
      </div>
    </section>
  );
}