import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import { Card, PageHeader, Spinner, useToast } from '../components/ui';
import { fmtDateTime } from '../utils/format';

export default function ParametersView() {
  const notify = useToast();
  const [params, setParams] = useState(null);
  const [editing, setEditing] = useState(null);
  const [value, setValue] = useState('');

  const load = useCallback(() => api.get('/parameters').then(setParams).catch((e) => notify(e.message, 'error')), [notify]);
  useEffect(() => { load(); }, [load]);

  const save = async (key) => {
    try {
      await api.put(`/parameters/${key}`, { value });
      notify('Parámetro actualizado.', 'success');
      setEditing(null);
      load();
    } catch (e) { notify(e.message, 'error'); }
  };

  if (!params) return <Spinner />;
  const groups = params.reduce((acc, p) => ({ ...acc, [p.category]: [...(acc[p.category] || []), p] }), {});

  return (
    <div>
      <PageHeader title="Parámetros del sistema" subtitle="Configuración de seguridad y límites. Las reglas metodológicas de SPADIES son fijas para que las cifras sean comparables con las oficiales." />
      {Object.entries(groups).map(([cat, items]) => (
        <Card key={cat} title={cat.charAt(0) + cat.slice(1).toLowerCase()}>
          <div className="param-grid">
            {items.map((p) => (
              <div key={p.key} className="param">
                <div className="param-desc">{p.description}</div>
                <code className="muted small">{p.key}</code>
                {editing === p.key ? (
                  <div className="btn-row">
                    <input type={p.data_type === 'INTEGER' ? 'number' : 'text'} min={p.min ?? undefined} max={p.max ?? undefined}
                      value={value} onChange={(e) => setValue(e.target.value)} autoFocus />
                    <button className="btn btn-primary btn-sm" onClick={() => save(p.key)}>Guardar</button>
                    <button className="btn btn-light btn-sm" onClick={() => setEditing(null)}>Cancelar</button>
                  </div>
                ) : (
                  <div className="param-value">
                    <strong>{p.value}</strong>
                    {p.is_editable && <button className="btn btn-light btn-sm" onClick={() => { setEditing(p.key); setValue(p.value); }}>Modificar</button>}
                  </div>
                )}
                <div className="muted small">
                  {p.min !== null && p.min !== undefined && `Rango ${p.min}–${p.max} · `}Por defecto {p.default_value} · {p.updated_by} · {fmtDateTime(p.updated_at)}
                </div>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}
