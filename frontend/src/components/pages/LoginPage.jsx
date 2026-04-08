import LoginForm from '../forms/LoginForm';

export default function LoginPage() {
  return (
    <section className="login-page">
      <div className="login-box">
        <div className="login-header">
          <p className="login-tag">Domus Gestor</p>
          <h1>Iniciar sesión</h1>
          <p className="login-subtitle">
            Accede a la plataforma de gestión de alojamientos turísticos,
            reservas, propietarios e inquilinos.
          </p>
        </div>

        <LoginForm />
      </div>
    </section>
  );
}