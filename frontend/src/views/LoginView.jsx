import { useState } from 'react';
import { api } from '../api/client';
import { Alert, Field } from '../components/ui';

export default function LoginView({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const res = await api.login(username.trim(), password);
      onLogin(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <img src="/logo-uco.svg" alt="Universidad Católica de Oriente" className="login-logo" />
        <div className="login-tag">Analítica de deserción y permanencia</div>
        <form className="form" onSubmit={submit}>
          <Field label="Usuario (cédula)">
            <input autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
          </Field>
          <Field label="Contraseña">
            <input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </Field>
          {error && <Alert type="error">{error}</Alert>}
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Ingresando…' : 'Iniciar sesión'}</button>
        </form>
        <p className="muted small center">¿Olvidó su contraseña? Solicite al administrador que la restablezca.</p>
      </div>
    </div>
  );
}
