import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge, Card, Empty, Field, Modal, PageHeader, TempPasswordNotice, useToast } from '../components/ui';
import { fmtDateTime } from '../utils/format';

const EMPTY = { username: '', nombre: '', role: 'consultor', activo: true };

function UserForm({ initial, onCancel, onSave, editing }) {
  const [f, setF] = useState(initial);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });
  return (
    <Modal title={editing ? 'Editar usuario' : 'Nuevo usuario'} onClose={onCancel}
      footer={<>
        <button className="btn btn-light" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" onClick={() => onSave(f)}>Guardar</button>
      </>}>
      <div className="form">
        <Field label="Usuario (cédula)" hint="4 a 30 caracteres: letras, números, punto, guion.">
          <input value={f.username} onChange={set('username')} autoFocus />
        </Field>
        <Field label="Nombre completo"><input value={f.nombre} onChange={set('nombre')} /></Field>
        <Field label="Rol" hint="Consultor: ve indicadores y estudiantes. Administrador: además gestiona usuarios, cargas y parámetros.">
          <select value={f.role} onChange={set('role')}>
            <option value="consultor">Consultor</option>
            <option value="administrador">Administrador</option>
          </select>
        </Field>
        {editing && (
          <label className="check"><input type="checkbox" checked={f.activo} onChange={set('activo')} /> Usuario activo (puede iniciar sesión)</label>
        )}
        {!editing && <p className="muted small">El sistema generará una contraseña temporal que el usuario deberá cambiar al ingresar.</p>}
      </div>
    </Modal>
  );
}

export default function UsersView({ currentUser }) {
  const notify = useToast();
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState(null);
  const [temp, setTemp] = useState(null);

  const load = useCallback(() => api.get('/users').then(setUsers).catch((e) => notify(e.message, 'error')), [notify]);
  useEffect(() => { load(); }, [load]);

  const save = async (f) => {
    try {
      if (form.id) {
        await api.put(`/users/${form.id}`, f);
        notify('Usuario actualizado.', 'success');
      } else {
        const res = await api.post('/users', f);
        setTemp({ username: res.user.username, password: res.temporary_password });
      }
      setForm(null);
      load();
    } catch (e) {
      notify(e.message, 'error');
    }
  };

  const reset = async (u) => {
    if (!window.confirm(`¿Restablecer la contraseña de ${u.nombre}? Se cerrarán sus sesiones abiertas.`)) return;
    try {
      const res = await api.post(`/users/${u.id}/reset-password`);
      setTemp({ username: u.username, password: res.temporary_password });
      load();
    } catch (e) { notify(e.message, 'error'); }
  };

  const remove = async (u) => {
    if (!window.confirm(`¿Eliminar definitivamente al usuario ${u.nombre} (${u.username})?`)) return;
    try {
      await api.del(`/users/${u.id}`);
      notify('Usuario eliminado.', 'success');
      load();
    } catch (e) { notify(e.message, 'error'); }
  };

  const q = search.trim().toLowerCase();
  const filtered = users.filter((u) => !q || u.username.toLowerCase().includes(q) || u.nombre.toLowerCase().includes(q));

  return (
    <div>
      <PageHeader title="Usuarios" subtitle="Cuentas de acceso y roles."
        actions={<button className="btn btn-primary" onClick={() => setForm({ ...EMPTY })}>＋ Nuevo usuario</button>} />
      <Card actions={<input type="search" placeholder="Buscar por nombre o cédula…" value={search} onChange={(e) => setSearch(e.target.value)} />}
        title={`Usuarios registrados (${filtered.length})`}>
        {filtered.length === 0 ? <Empty>No hay usuarios para mostrar.</Empty> : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Usuario</th><th>Nombre</th><th>Rol</th><th>Estado</th><th>Último ingreso</th><th /></tr></thead>
              <tbody>
                {filtered.map((u) => (
                  <tr key={u.id}>
                    <td><strong>{u.username}</strong></td>
                    <td>{u.nombre}</td>
                    <td><Badge tone={u.role === 'administrador' ? 'success' : 'neutral'}>{u.role}</Badge></td>
                    <td>
                      {!u.activo ? <Badge tone="danger">Inactivo</Badge>
                        : u.debe_cambiar_clave ? <Badge tone="warning">Clave temporal</Badge> : <Badge tone="success">Activo</Badge>}
                    </td>
                    <td>{fmtDateTime(u.ultimo_ingreso)}</td>
                    <td className="actions">
                      <button className="btn btn-light btn-sm" onClick={() => setForm({ id: u.id, username: u.username, nombre: u.nombre, role: u.role, activo: u.activo })}>Editar</button>
                      <button className="btn btn-light btn-sm" onClick={() => reset(u)}>Restablecer clave</button>
                      {u.id !== currentUser.id && <button className="btn btn-danger btn-sm" onClick={() => remove(u)}>Eliminar</button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
      {form && <UserForm initial={form} editing={Boolean(form.id)} onCancel={() => setForm(null)} onSave={save} />}
      {temp && <TempPasswordNotice username={temp.username} password={temp.password} onClose={() => setTemp(null)} />}
    </div>
  );
}
