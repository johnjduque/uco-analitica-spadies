import { useEffect, useMemo, useRef, useState } from 'react';
import { api, qs } from '../api/client';

/**
 * Selector múltiple de programas con datos cargados para el nivel elegido.
 * value = [] significa "todos los programas del nivel".
 */
export default function ProgramPicker({ nivel, value, onChange }) {
  const [programs, setPrograms] = useState([]);
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [draft, setDraft] = useState(value);
  const boxRef = useRef(null);

  useEffect(() => {
    let alive = true;
    api.get(`/indicators/programs${qs({ nivel })}`)
      .then((data) => alive && setPrograms(data))
      .catch(() => alive && setPrograms([]));
    return () => { alive = false; };
  }, [nivel]);

  useEffect(() => { setDraft(value); }, [value]);

  useEffect(() => {
    const onDoc = (e) => { if (open && boxRef.current && !boxRef.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [open]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return programs.filter((p) => !q || p.nombre.toLowerCase().includes(q));
  }, [programs, search]);

  const toggle = (name) => setDraft((d) => (d.includes(name) ? d.filter((x) => x !== name) : [...d, name]));
  const apply = () => { onChange(draft); setOpen(false); };

  const label = value.length === 0
    ? `Todos los programas (${programs.length})`
    : value.length === 1 ? value[0] : `${value.length} programas seleccionados`;

  return (
    <div className="picker" ref={boxRef}>
      <button type="button" className="picker-trigger" onClick={() => setOpen(!open)} aria-expanded={open}>
        <span className="picker-label">{label}</span>
        <span className="muted">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="picker-panel">
          <input type="search" placeholder="Buscar programa…" value={search} onChange={(e) => setSearch(e.target.value)} autoFocus />
          <div className="picker-tools">
            <button type="button" className="link" onClick={() => setDraft([])}>Todos</button>
            <button type="button" className="link" onClick={() => setDraft(filtered.map((p) => p.nombre))}>Seleccionar visibles</button>
          </div>
          <div className="picker-list">
            {filtered.map((p) => (
              <label key={p.id} className={`picker-item ${draft.includes(p.nombre) ? 'checked' : ''}`}>
                <input type="checkbox" checked={draft.includes(p.nombre)} onChange={() => toggle(p.nombre)} />
                <span>{p.nombre}</span>
                {nivel === 'todos' && <span className="badge badge-neutral">{p.nivel}</span>}
              </label>
            ))}
            {filtered.length === 0 && <div className="muted small">No hay programas con datos para este filtro.</div>}
          </div>
          <div className="picker-foot">
            <span className="muted small">{draft.length === 0 ? 'Se incluirán todos' : `${draft.length} seleccionados`}</span>
            <button type="button" className="btn btn-primary btn-sm" onClick={apply}>Aplicar</button>
          </div>
        </div>
      )}
    </div>
  );
}
