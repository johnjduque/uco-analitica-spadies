import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import { Alert, Badge, Card, Field, Modal, PageHeader, Segmented, useToast } from '../components/ui';

const FILTERS = [{ id: 'todos', label: 'Todos' }, { id: 'pregrado', label: 'Pregrado' }, { id: 'posgrado', label: 'Posgrado' }];

export default function ProgramsView() {
  const notify = useToast();
  const [programs, setPrograms] = useState([]);
  const [filter, setFilter] = useState('todos');
  const [search, setSearch] = useState('');
  const [edit, setEdit] = useState(null);

  const load = useCallback(() => api.get('/programs').then(setPrograms).catch((e) => notify(e.message, 'error')), [notify]);
  useEffect(() => { load(); }, [load]);

  const save = async () => {
    try {
      if (edit.id) await api.put(`/programs/${edit.id}`, { nombre: edit.nombre, nivel: edit.nivel, codigo: edit.codigo || '', activo: edit.activo });
      else await api.post('/programs', { nombre: edit.nombre, nivel: edit.nivel, codigo: edit.codigo || null });
      notify('Catálogo actualizado. Los indicadores se recalculan con el nuevo nivel.', 'success');
      setEdit(null);
      load();
    } catch (e) { notify(e.message, 'error'); }
  };

  const q = search.trim().toLowerCase();
  const rows = programs.filter((p) => (filter === 'todos' || p.nivel === filter) && (!q || p.nombre.toLowerCase().includes(q) || (p.codigo || '').toLowerCase().includes(q)));

  return (
    <div>
      <PageHeader title="Catálogo de programas" subtitle="Nivel de formación de cada programa y códigos institucionales."
        actions={<button className="btn btn-primary" onClick={() => setEdit({ nombre: '', nivel: 'pregrado', codigo: '', activo: true })}>＋ Nuevo programa</button>} />
      <Alert type="info">El <strong>nivel</strong> de cada programa determina si sus estudiantes se cuentan en los indicadores de pregrado o de posgrado. Revíselo cuando se cree un programa nuevo.</Alert>
      <Card title={`Programas (${rows.length})`}
        actions={<div className="btn-row"><Segmented options={FILTERS} value={filter} onChange={setFilter} ariaLabel="Nivel" />
          <input type="search" placeholder="Buscar…" value={search} onChange={(e) => setSearch(e.target.value)} /></div>}>
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Código</th><th>Programa</th><th>Nivel</th><th>Estado</th><th /></tr></thead>
            <tbody>
              {rows.map((p) => (
                <tr key={p.id}>
                  <td><code>{p.codigo || '—'}</code></td>
                  <td>{p.nombre}</td>
                  <td><Badge tone={p.nivel === 'posgrado' ? 'info' : 'success'}>{p.nivel}</Badge></td>
                  <td>{p.activo ? 'Activo' : <Badge tone="neutral">Inactivo</Badge>}</td>
                  <td><button className="btn btn-light btn-sm" onClick={() => setEdit({ ...p })}>Editar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      {edit && (
        <Modal title={edit.id ? 'Editar programa' : 'Nuevo programa'} onClose={() => setEdit(null)}
          footer={<><button className="btn btn-light" onClick={() => setEdit(null)}>Cancelar</button>
            <button className="btn btn-primary" onClick={save}>Guardar</button></>}>
          <div className="form">
            <Field label="Nombre oficial"><input value={edit.nombre} onChange={(e) => setEdit({ ...edit, nombre: e.target.value })} /></Field>
            <div className="inline-fields">
              <Field label="Código"><input value={edit.codigo || ''} maxLength={20} onChange={(e) => setEdit({ ...edit, codigo: e.target.value.toUpperCase() })} /></Field>
              <Field label="Nivel">
                <select value={edit.nivel} onChange={(e) => setEdit({ ...edit, nivel: e.target.value })}>
                  <option value="pregrado">Pregrado</option>
                  <option value="posgrado">Posgrado</option>
                </select>
              </Field>
            </div>
            {edit.id && <label className="check"><input type="checkbox" checked={edit.activo} onChange={(e) => setEdit({ ...edit, activo: e.target.checked })} /> Programa activo</label>}
          </div>
        </Modal>
      )}
    </div>
  );
}
