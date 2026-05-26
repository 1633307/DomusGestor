import { Link } from 'react-router-dom';
import LoginForm from '../forms/LoginForm';
import styles from './loginPage.module.css';
export default function LoginPage() {
  return (
    <section className={styles.loginPage}>
      <div className={styles.loginBox}>
        <div className={styles.loginHeader}>
          <p className={styles.loginTag}>Domus Gestor</p>
          <h1 className={styles.title}>Iniciar sessió</h1>
          <p className={styles.loginSubtitle}>
            Accedeix a la plataforma de gestió d'allotjaments turístics,
            reserves, propietaris i inquilins.
          </p>
        </div>

        <LoginForm />

        <div className={styles.clientEntry}>
          <span>Ets client?</span>
          <Link to="/login-clientes">Accedeix al portal de clients</Link>
        </div>
      </div>
    </section>
  );
}
