import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/authContext';

export default function LoginForm() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    nip: '',
    password: '',
  });

  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    try {
      login(form);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <label>
        NIP
        <input
          type="text"
          name="nip"
          value={form.nip}
          onChange={handleChange}
          placeholder="Introduce tu NIP"
        />
      </label>

      <label>
        Contraseña
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Introduce tu contraseña"
        />
      </label>

      {error && <p className="error-text">{error}</p>}

      <button type="submit" className="login-button">
        Entrar
      </button>
    </form>
  );
}