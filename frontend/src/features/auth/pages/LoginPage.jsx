import LoginForm from '../components/LoginForm';

export default function LoginPage() {
  return (
    <section className="login-page">
      <div className="login-hero">
        <h1>Domus Gestor</h1>
        <p>
          Plataforma para la gestión de alojamientos turísticos, reservas,
          propietarios e inquilinos.
        </p>
      </div>

      <div className="login-panel">
        <LoginForm />
      </div>
    </section>
  );
}