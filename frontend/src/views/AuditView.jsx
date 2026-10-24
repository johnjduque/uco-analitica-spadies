import { useEffect, useState } from 'react';
import { api, qs } from '../api/client';
import { Badge, Card, Empty, PageHeader, Pagination, Spinner } from '../components/ui';
import { fmtDateTime } from '../utils/format';

const ACTIONS = ['LOGIN_EXITOSO', 'LOGIN_FALLIDO', 'CREAR', 'EDITAR', 'ELIMINAR', 'CAMBIO_CLAVE', 'RESTABLECER_CLAVE',
  'CARGA_DATOS', 'PURGA_DATOS', 'EXPORTAR', 'CONSULTA'];
const ENTITIES = ['USUARIO', 'ARCHIVO_DATOS', 'PARAMETRO', 'PROGRAMA', 'REPORTE', 'ESTUDIANTE'];
const TONE = { LOGIN_FALLIDO: 'danger', ELIMINAR: 'danger', PURGA_DATOS: 'danger', LOGIN_EXITOSO: 'success', CREAR: 'info', CARGA_DATOS: 'info' };

function details(raw) {
  if (!raw) return '—';
  if (raw.trim().startsWith('{')) {
    try {
      const d = JSON.parse(raw);
      if (d.antes && d.despues) {
        const changes = Object.keys(d.despues).filter((k) => JSON.stringify(d.antes[k]) !== JSON.stringify(d.despues[k]));
        return changes.length ? changes.map((k) => `${k}: ${d.antes[k]} → ${d.despues[k]}`).join(' · ') : 'Sin cambios';
      }
    } catch { /* texto plano */ }
  }
  return raw;
}

export default function AuditView() {
  const [page, setPage] = useState(1);
  const [action, setAction] = useState('');
  const [entity, setEntity] = useState('');
  const [search, setSearch] = useState('');
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);

  useEffect(() => {
    let alive = true;
    api.get(`/audit-logs${qs({ page, limit: 25, action, entity, search: query })}`).then((d) => alive && setData(d)).catch(() => {});
    return () => { alive = false; };
  }, [page, action, entity, query]);

  return (
    <div>
      <PageHeader title="Auditoría" subtitle="Registro cronológico de accesos, cambios, cargas, descargas y consultas individuales." />
      <Card>
        <form className="filter-row" onSubmit={(e) => { e.preventDefault(); setPage(1); setQuery(search); }}>
          <input type="search" placeholder="Buscar por usuario o detalle…" value={search} onChange={(e) => setSearch(e.target.value)} />
          <select value={action} onChange={(e) => { setAction(e.target.value); setPage(1); }}>
            <option value="">Todas las acciones</option>
            {ACTIONS.map((a) => <option key={a} value={a}>{a.replace('_', ' ').toLowerCase()}</option>)}
          </select>
          <select value={entity} onChange={(e) => { setEntity(e.target.value); setPage(1); }}>
            <option value="">Todas las entidades</option>
            {ENTITIES.map((a) => <option key={a} value={a}>{a.replace('_', ' ').toLowerCase()}</option>)}
          </select>
          <button className="btn btn-primary">Buscar</button>
        </form>
      </Card>
      <Card>
        {!data ? <Spinner /> : data.items.length === 0 ? <Empty>Sin registros para el filtro.</Empty> : (
          <>
            <div className="table-wrap">
              <table className="table">
                <thead><tr><th>Fecha</th><th>Usuario</th><th>Acción</th><th>Entidad</th><th>IP</th><th>Detalle</th></tr></thead>
                <tbody>
                  {data.items.map((l) => (
                    <tr key={l.id}>
                      <td className="nowrap">{fmtDateTime(l.timestamp)}</td>
                      <td><strong>{l.user_name}</strong><div className="muted small">{l.username} · {l.user_role}</div></td>
                      <td><Badge tone={TONE[l.action] || 'neutral'}>{l.action}</Badge></td>
                      <td>{l.entity}{l.entity_id ? ` #${l.entity_id}` : ''}</td>
                      <td className="mono small">{l.ip_address}</td>
                      <td className="wrap">{details(l.details)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={data.page} totalPages={data.total_pages} total={data.total} onChange={setPage} />
          </>
        )}
      </Card>
    </div>
  );
}
