import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import { Alert, Badge, Card, Empty, Field, Modal, PageHeader, Spinner, useToast } from '../components/ui';
import { fmtDateTime, fmtNum } from '../utils/format';

const TIPOS = [
  { id: 'matriculados', label: 'Matriculados', file: 'Matriculados', help: 'Todos los estudiantes matriculados en el semestre.' },
  { id: 'nuevos', label: 'Matriculados nuevos (primíparos)', file: 'Matriculados Nuevos', help: 'Estudiantes que ingresan por primera vez. Definen las cohortes.' },
  { id: 'egresados', label: 'Egresados / graduados', file: 'Egresados', help: 'Graduados con su fecha de grado. Puede cargarse por semestre o por año completo.' },
];
const TIPO_LABEL = Object.fromEntries(TIPOS.map((t) => [t.id, t.label]));

function splitPeriod(p) {
  if (!p) return { year: new Date().getFullYear(), sem: '1' };
  const [y, s] = p.split('-');
  return { year: Number(y), sem: s || 'anual' };
}

function ProgramDecisionModal({ pending, programs, onCancel, onConfirm }) {
  const [rows, setRows] = useState(() => pending.map((p) => ({
    nombre: p.nombre, filas: p.filas, accion: 'crear', nivel: p.nivel_sugerido, nombre_oficial: p.nombre, programa_id: '',
  })));
  const set = (i, patch) => setRows((r) => r.map((x, k) => (k === i ? { ...x, ...patch } : x)));
  const valid = rows.every((r) => (r.accion === 'crear' ? r.nombre_oficial.trim().length >= 2 : r.programa_id));
  return (
    <Modal wide title="Programas no reconocidos" onClose={onCancel}
      footer={<>
        <button className="btn btn-light" onClick={onCancel}>Cancelar carga</button>
        <button className="btn btn-primary" disabled={!valid} onClick={() => onConfirm(rows.map((r) => ({
          nombre: r.nombre, accion: r.accion, nivel: r.nivel, nombre_oficial: r.nombre_oficial.trim(),
          programa_id: r.programa_id ? Number(r.programa_id) : undefined,
        })))}>Confirmar y cargar</button>
      </>}>
      <p>El archivo contiene programas que no están en el catálogo. Indique para cada uno si es un <strong>programa nuevo</strong> o una
        forma distinta de escribir un <strong>programa existente</strong>. La decisión se recuerda para próximas cargas.</p>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Texto en el archivo</th><th className="num">Filas</th><th>Decisión</th><th>Detalle</th></tr></thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={r.nombre}>
                <td><code>{r.nombre}</code></td>
                <td className="num">{fmtNum(r.filas)}</td>
                <td>
                  <select value={r.accion} onChange={(e) => set(i, { accion: e.target.value })}>
                    <option value="crear">Es un programa nuevo</option>
                    <option value="asociar">Es un programa existente</option>
                  </select>
                </td>
                <td>
                  {r.accion === 'crear' ? (
                    <div className="inline-fields">
                      <input value={r.nombre_oficial} onChange={(e) => set(i, { nombre_oficial: e.target.value })} placeholder="Nombre oficial" />
                      <select value={r.nivel} onChange={(e) => set(i, { nivel: e.target.value })}>
                        <option value="pregrado">Pregrado</option>
                        <option value="posgrado">Posgrado</option>
                      </select>
                    </div>
                  ) : (
                    <select value={r.programa_id} onChange={(e) => set(i, { programa_id: e.target.value })}>
                      <option value="">Seleccione el programa…</option>
                      {programs.map((p) => <option key={p.id} value={p.id}>{p.nombre} ({p.nivel})</option>)}
                    </select>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Modal>
  );
}

export default function LoadsView() {
  const notify = useToast();
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [tipo, setTipo] = useState('matriculados');
  const [year, setYear] = useState(new Date().getFullYear());
  const [sem, setSem] = useState('1');
  const [file, setFile] = useState(null);
  const [replace, setReplace] = useState(false);
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState(null);
  const [programs, setPrograms] = useState([]);
  const [lastResult, setLastResult] = useState(null);
  const [fileKey, setFileKey] = useState(0);

  const refresh = useCallback(async () => {
    try {
      const [st, hist] = await Promise.all([api.get('/loads/status'), api.get('/loads')]);
      setStatus(st);
      setHistory(hist);
      return st;
    } catch (e) {
      notify(e.message, 'error');
      return null;
    }
  }, [notify]);

  const applySuggestion = (st) => {
    if (!st?.siguiente) return;
    setTipo(st.siguiente.tipo);
    if (st.siguiente.periodo) {
      const p = splitPeriod(st.siguiente.periodo);
      setYear(p.year);
      setSem(p.sem);
    }
  };

  useEffect(() => {
    refresh().then((st) => applySuggestion(st));
  }, [refresh]);

  const periodo = sem === 'anual' ? String(year) : `${year}-${sem}`;

  const send = async (decisiones) => {
    const form = new FormData();
    form.append('file', file);
    form.append('tipo', tipo);
    form.append('periodo', periodo);
    form.append('reemplazar', replace ? 'true' : 'false');
    if (decisiones) form.append('decisiones_programas', JSON.stringify(decisiones));
    setBusy(true);
    try {
      const res = await api.upload('/loads', form);
      if (res.status === 'confirmar_programas') {
        setPrograms(await api.get('/programs'));
        setPending(res.programas);
        return;
      }
      setPending(null);
      setLastResult(res);
      notify(`✅ ${res.message} (${fmtNum(res.registros)} registros)`, 'success');
      setFile(null);
      setReplace(false);
      setFileKey((k) => k + 1);
      setStatus(res.estado);
      setHistory(await api.get('/loads'));
      applySuggestion(res.estado);
    } catch (e) {
      notify(e.message, 'error', 15000);
    } finally {
      setBusy(false);
    }
  };

  const submit = (e) => {
    e.preventDefault();
    if (!file) { notify('Seleccione un archivo.', 'warning'); return; }
    send();
  };

  const remove = async (load) => {
    if (!window.confirm(`¿Eliminar la carga de ${TIPO_LABEL[load.tipo]} ${load.periodo}? Sus registros se borrarán de los indicadores.`)) return;
    try {
      const res = await api.del(`/loads/${load.id}`);
      notify(res.message, 'success');
      refresh();
    } catch (e) {
      notify(e.message, 'error', 10000);
    }
  };

  const tipoInfo = TIPOS.find((t) => t.id === tipo);
  const expectedName = `${tipoInfo.file} ${sem === 'anual' ? year : `${sem}-${year}`}.xlsx`;

  return (
    <div>
      <PageHeader title="Carga de información" subtitle="Archivos institucionales de matriculados, matriculados nuevos y egresados, por periodo." />

      <div className="grid-2">
        <Card title="Cargar archivo">
          {status?.siguiente?.periodo && (
            <Alert type="info">
              Siguiente carga sugerida: <strong>{TIPO_LABEL[status.siguiente.tipo]} {status.siguiente.periodo}</strong>{' '}
              <button type="button" className="link" onClick={() => applySuggestion(status)}>Usar sugerencia</button>
            </Alert>
          )}
          <form onSubmit={submit} className="form">
            <Field label="Tipo de archivo" hint={tipoInfo.help}>
              <select value={tipo} onChange={(e) => { setTipo(e.target.value); if (e.target.value !== 'egresados' && sem === 'anual') setSem('1'); }}>
                {TIPOS.map((t) => <option key={t.id} value={t.id}>{t.label}</option>)}
              </select>
            </Field>
            <div className="inline-fields">
              <Field label="Año">
                <input type="number" min="1990" max="2100" value={year} onChange={(e) => setYear(Number(e.target.value))} />
              </Field>
              <Field label="Semestre">
                <select value={sem} onChange={(e) => setSem(e.target.value)}>
                  <option value="1">1 (enero–junio)</option>
                  <option value="2">2 (julio–diciembre)</option>
                  {tipo === 'egresados' && <option value="anual">Año completo</option>}
                </select>
              </Field>
            </div>
            <Field label="Archivo (.xlsx, .xls o .csv)" hint={`Nombre recomendado: "${expectedName}". Si el nombre indica otro periodo, la carga se rechaza para evitar errores.`}>
              <input key={fileKey} type="file" accept=".xlsx,.xls,.csv" onChange={(e) => setFile(e.target.files[0] || null)} />
            </Field>
            <label className="check">
              <input type="checkbox" checked={replace} onChange={(e) => setReplace(e.target.checked)} />
              Reemplazar el archivo existente de este tipo y periodo (para corregir una carga)
            </label>
            <button className="btn btn-primary" disabled={busy}>{busy ? 'Procesando…' : `Cargar ${tipoInfo.label.toLowerCase()} ${periodo}`}</button>
          </form>
          {lastResult?.advertencias?.length > 0 && (
            <Alert type="warning" title="Observaciones de la última carga:">
              <ul>{lastResult.advertencias.map((w) => <li key={w}>{w}</li>)}</ul>
            </Alert>
          )}
        </Card>

        <Card title="Reglas de carga">
          <ul className="rules">
            <li><strong>Matriculados</strong> debe cargarse en periodos consecutivos (sin saltos). Se puede agregar historia anterior al primer periodo.</li>
            <li><strong>Matriculados nuevos</strong> requiere que el periodo de matriculados ya esté cargado. Sin este archivo no se calcula la cohorte.</li>
            <li><strong>Egresados</strong> se carga por semestre o por año completo (no ambos para el mismo año). El semestre de cada grado se toma del mes de la fecha de grado (enero–junio = 1).</li>
            <li>Columnas requeridas: número de documento y programa; en egresados, además, la fecha de grado. Los nombres de columna pueden variar.</li>
            <li>Los programas se reconocen por código (ej. <code>IS</code>) o nombre. Si aparece uno desconocido, el sistema pregunta antes de cargar.</li>
          </ul>
        </Card>
      </div>

      <Card title="Estado por periodo">
        {!status ? <Spinner /> : status.periodos.length === 0 ? (
          <Empty>Aún no hay información cargada. Empiece por el archivo de Matriculados del periodo más antiguo disponible.</Empty>
        ) : (
          <>
            <div className="table-wrap">
              <table className="table">
                <thead><tr><th>Periodo</th><th className="num">Matriculados</th><th className="num">Nuevos</th><th className="num">Egresados</th></tr></thead>
                <tbody>
                  {status.periodos.map((p) => (
                    <tr key={p.periodo}>
                      <td><strong>{p.periodo}</strong></td>
                      <td className="num">{p.matriculados === null ? <Badge tone="danger">Falta</Badge> : fmtNum(p.matriculados)}</td>
                      <td className="num">{p.nuevos === null ? <Badge tone="warning">Falta</Badge> : fmtNum(p.nuevos)}</td>
                      <td className="num">{p.egresados === null ? <Badge tone="warning">Falta</Badge>
                        : <>{fmtNum(p.egresados)} {p.egresados_modo === 'anual' && <Badge>anual</Badge>}</>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {status.advertencias.length > 0 && (
              <details className="alert alert-warning">
                <summary>{status.advertencias.length} advertencias de datos faltantes</summary>
                <ul>{status.advertencias.map((w) => <li key={w}>{w}</li>)}</ul>
              </details>
            )}
          </>
        )}
      </Card>

      <Card title={`Historial de cargas (${history.length})`}>
        {history.length === 0 ? <Empty>Sin cargas registradas.</Empty> : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Tipo</th><th>Periodo</th><th>Archivo</th><th className="num">Registros</th><th>Cargado por</th><th>Fecha</th><th /></tr></thead>
              <tbody>
                {history.map((l) => (
                  <tr key={l.id}>
                    <td>{TIPO_LABEL[l.tipo] || l.tipo}</td>
                    <td><strong>{l.periodo}</strong></td>
                    <td className="truncate" title={l.archivo_nombre}>{l.archivo_nombre}</td>
                    <td className="num">{fmtNum(l.registros)}</td>
                    <td>{l.cargado_por || '—'}</td>
                    <td>{fmtDateTime(l.created_at)}</td>
                    <td><button className="btn btn-danger btn-sm" onClick={() => remove(l)}>Eliminar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {pending && (
        <ProgramDecisionModal pending={pending} programs={programs}
          onCancel={() => { setPending(null); notify('Carga cancelada.', 'info'); }}
          onConfirm={(dec) => send(dec)} />
      )}
    </div>
  );
}
