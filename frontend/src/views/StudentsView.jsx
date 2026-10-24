import { useEffect, useState } from 'react';
import { api, qs } from '../api/client';
import ProgramPicker from '../components/ProgramPicker';
import { Alert, Badge, Card, Empty, PageHeader, Pagination, Segmented, Spinner } from '../components/ui';
import { fmtNum, NIVELES } from '../utils/format';

const STATE_TONE = { Activo: 'success', Desertor: 'danger', Graduado: 'info' };
const LIMIT = 25;

function StudentDetail({ data, onClose }) {
  return (
    <Card title={`Trayectoria del documento ${data.documento}`} actions={<button className="btn btn-light btn-sm" onClick={onClose}>Cerrar</button>}>
      <div className="detail-head">
        <div>
          <p><strong>Programa:</strong> {data.programa || '—'}</p>
          <p className="muted">Periodos matriculado: <strong>{data.periodos_matriculado}</strong> · Última matrícula: <strong>{data.ultimo_periodo || '—'}</strong> · Corte: {data.periodo_corte}</p>
          {data.grados.length > 0 && (
            <p className="muted">Grados: {data.grados.map((g) => `${g.programa} (${g.fecha || g.periodo})`).join(' · ')}</p>
          )}
        </div>
        <div className={`state-pill state-${data.estado.toLowerCase()}`}>
          <span>{data.estado}</span>
          <small>Estado SPADIES</small>
        </div>
      </div>
      <p className="muted small">{data.definicion}</p>
      <div className="timeline">
        {data.trayectoria.map((t) => (
          <div key={t.periodo} className={`tl-item ${t.matriculado ? 'on' : 'off'} ${t.grados.length ? 'grad' : ''}`}>
            <span className="tl-period">{t.periodo}</span>
            <span className="tl-dot" />
            <span className="tl-text">
              {t.matriculado ? t.programas.join(' · ') : 'Sin matrícula'}
              {t.nuevo_en.length > 0 && <Badge tone="warning">Primíparo</Badge>}
              {t.grados.map((g) => <Badge key={g.programa} tone="info">Grado {g.fecha || ''}</Badge>)}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default function StudentsView() {
  const [nivel, setNivel] = useState('pregrado');
  const [programas, setProgramas] = useState([]);
  const [estado, setEstado] = useState('Todos');
  const [search, setSearch] = useState('');
  const [debounced, setDebounced] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [doc, setDoc] = useState('');
  const [detail, setDetail] = useState(null);
  const [detailError, setDetailError] = useState('');

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 350);
    return () => clearTimeout(t);
  }, [search]);

  useEffect(() => {
    let alive = true;
    api.get(`/students/summary${qs({ nivel, estado, buscar: debounced, programas: programas.join('|'), page, limit: LIMIT })}`)
      .then((d) => { if (alive) { setData(d); setError(''); } })
      .catch((e) => alive && setError(e.message));
    return () => { alive = false; };
  }, [nivel, estado, debounced, programas, page]);

  const lookup = async (value) => {
    const v = (value ?? doc).trim();
    if (!v) return;
    setDetailError('');
    try {
      setDetail(await api.get(`/students/${encodeURIComponent(v)}`));
      setDoc(v);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e) {
      setDetail(null);
      setDetailError(e.message);
    }
  };

  const total = data?.total_estudiantes || 0;
  const filters = [
    { id: 'Todos', label: `Todos (${fmtNum(total)})` },
    ...['Activo', 'Desertor', 'Graduado'].map((s) => ({
      id: s, label: `${s}s (${fmtNum(data?.resumen?.[s]?.cantidad || 0)} · ${(data?.resumen?.[s]?.porcentaje ?? 0).toFixed(1)}%)`,
    })),
  ];

  return (
    <div>
      <PageHeader title="Estado por estudiante" subtitle="Clasificación SPADIES (Activo, Desertor, Graduado) al último periodo cargado y trayectoria individual." />

      <Card>
        <form className="search-row" onSubmit={(e) => { e.preventDefault(); lookup(); }}>
          <input type="search" placeholder="Número de documento del estudiante" value={doc} onChange={(e) => setDoc(e.target.value)} />
          <button className="btn btn-primary">Consultar trayectoria</button>
        </form>
        {detailError && <Alert type="warning">{detailError}</Alert>}
      </Card>

      {detail && <StudentDetail data={detail} onClose={() => setDetail(null)} />}

      <Card className="filters">
        <div className="filter-row">
          <div className="filter">
            <span className="field-label">Nivel de formación</span>
            <Segmented options={NIVELES} value={nivel} onChange={(n) => { setNivel(n); setProgramas([]); setPage(1); }} ariaLabel="Nivel" />
          </div>
          <div className="filter filter-grow">
            <span className="field-label">Programas</span>
            <ProgramPicker nivel={nivel} value={programas} onChange={(p) => { setProgramas(p); setPage(1); }} />
          </div>
        </div>
      </Card>

      {error && <Alert type="error">{error}</Alert>}
      {!data ? <Spinner /> : total === 0 ? <Empty>No hay estudiantes para este filtro.</Empty> : (
        <>
          <div className="kpis">
            <div className="kpi"><span className="kpi-label">Estudiantes evaluados</span><span className="kpi-value">{fmtNum(total)}</span><span className="kpi-detail">Corte {data.periodo_corte}</span></div>
            {['Activo', 'Desertor', 'Graduado'].map((s) => (
              <div key={s} className={`kpi kpi-${STATE_TONE[s]}`}>
                <span className="kpi-label">{s}s</span>
                <span className="kpi-value">{fmtNum(data.resumen[s].cantidad)}</span>
                <span className="kpi-detail">{data.resumen[s].porcentaje.toFixed(2)}% · {data.definiciones[s]}</span>
              </div>
            ))}
          </div>
          <Card title={`Listado (${fmtNum(data.total_filtrados)})`}
            actions={<input type="search" placeholder="Filtrar por documento o programa…" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />}>
            <Segmented options={filters} value={estado} onChange={(s) => { setEstado(s); setPage(1); }} ariaLabel="Estado" />
            <div className="table-wrap">
              <table className="table">
                <thead><tr><th>Documento</th><th>Programa</th><th>Última matrícula</th><th>Estado</th><th /></tr></thead>
                <tbody>
                  {data.estudiantes.map((s) => (
                    <tr key={s.documento}>
                      <td><strong>{s.documento}</strong></td>
                      <td>{s.programa}</td>
                      <td>{s.ultimo_periodo || '—'}</td>
                      <td><Badge tone={STATE_TONE[s.estado]}>{s.estado}</Badge></td>
                      <td><button className="btn btn-light btn-sm" onClick={() => lookup(s.documento)}>Ver trayectoria</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={page} totalPages={Math.max(1, Math.ceil(data.total_filtrados / LIMIT))} total={data.total_filtrados} onChange={setPage} />
          </Card>
        </>
      )}
    </div>
  );
}
