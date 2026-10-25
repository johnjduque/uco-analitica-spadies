import { useState } from 'react';
import { api } from '../api/client';
import { Alert, Field, PasswordInput } from '../components/ui';

/**
 * Cambio de contraseña del usuario autenticado.
 * forced = true cuando el sistema exige cambiar la contraseña temporal.
 */
export default function ChangePasswordView({ forced = false, onChanged }) {
  const [oldPwd, setOldPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [ok, setOk] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(''); setOk('');
    if (newPwd !== confirm) { setError('La confirmación no coincide con la nueva contraseña.'); return; }
    setBusy(true);
    try {
      const res = await api.post('/auth/change-password', { old_password: oldPwd, new_password: newPwd });
      setOldPwd(''); setNewPwd(''); setConfirm('');
      setOk('Contraseña actualizada.');
      onChanged?.(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="form narrow" onSubmit={submit}>
      {forced && <Alert type="warning">Por seguridad debe reemplazar la contraseña temporal o por defecto antes de continuar.</Alert>}
      <Field label={forced ? 'Contraseña temporal / actual' : 'Contraseña actual'}>
        <PasswordInput autoComplete="current-password" value={oldPwd} onChange={(e) => setOldPwd(e.target.value)} required />
      </Field>
      <Field label="Nueva contraseña" hint="Mínimo 8 caracteres, con letras y números. No puede ser igual a su usuario.">
        <PasswordInput autoComplete="new-password" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} required />
      </Field>
      <Field label="Confirmar nueva contraseña">
        <PasswordInput autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
      </Field>
      {error && <Alert type="error">{error}</Alert>}
      {ok && <Alert type="success">{ok}</Alert>}
      <button className="btn btn-primary" disabled={busy}>{busy ? 'Guardando…' : 'Cambiar contraseña'}</button>
    </form>
  );
}
