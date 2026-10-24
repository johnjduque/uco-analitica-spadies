import { useEffect, useMemo, useState } from 'react';
import { api, qs } from '../api/client';
import LineChart, { SERIES_COLORS } from '../components/LineChart';
import ProgramPicker from '../components/ProgramPicker';
import { Alert, Card, Empty, PageHeader, Segmented, Spinner, useToast } from '../components/ui';
import { fmtNum, fmtPct, NIVELES, VISTAS } from '../utils/format';
import { INDICATOR_ORDER, INDICATORS } from './indicatorMeta';

const MAX_COHORTS = 8;

function Formula({ meta }) {
  return (
    <div className="formula">
      <span className="formula-sym">{meta.symbol}<sub>{meta.sub}</sub></span>
      <span className="formula-eq">=</span>
      <span className="formula-frac">
        <span>{meta.num}</span>
        <span className="formula-bar" />
        <span>{meta.den}</span>
      </span>
      <span className="formula-eq">× 100</span>
    </div>
  );
}

function Kpi({ label, value, detail }) {
  return (
    <div className="kpi">
      <span className="kpi-label">{label}</span>
      <span className="kpi-value">{value}</span>
      <span className="kpi-detail">{detail}</span>
    </div>
  );
}

const lastWith = (arr, minCohorts = 0) => [...(arr || [])].reverse()
  .find((x) => x.tasa !== null && x.tasa !== undefined && (x.cohortes === undefined || x.cohortes >= minCohorts));

function heat(v, max) {
  if (v === null || v === undefined || !max) return undefined;
  const a = Math.min(1, v / max) * 0.55;
  return { background: `rgba(227, 73, 72, ${a.toFixed(3)})` };
}

function PeriodTable({ rows, countKey, countLabel }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr><th>Periodo</th><th className="num">Base (matriculados)</th><th className="num">{countLabel}</th><th className="num">Tasa</th><th className="num">Retención</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.periodo}>
              <td><strong>{r.periodo}</strong></td>
              <td className="num">{fmtNum(r.base)}</td>
              <td className="num">{fmtNum(r[countKey])}</td>
              <td className="num"><strong>{fmtPct(r.tasa)}</strong></td>
              <td className="num">{fmtPct(r.retencion)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SemesterTable({ rows, countKey, countLabel }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr><th>Semestre</th><th className="num">Tasa</th><th className="num">{countLabel}</th><th className="num">Primíparos</th><th className="num">Cohortes</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.semestre}>
              <td><strong>S{r.semestre}</strong></td>
              <td className="num"><strong>{fmtPct(r.tasa)}</strong></td>
              <td className="num">{fmtNum(r[countKey])}</td>
              <td className="num">{fmtNum(r.primiparos)}</td>
              <td className="num">{r.cohortes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CohortMatrix({ matrix, selected, onToggle }) {
  const cols = Math.max(0, ...matrix.cohortes.map((c) => {
    const lastIdx = c.valores.map((v, i) => (v !== null ? i : -1)).reduce((a, b) => Math.max(a, b), -1);
    return lastIdx + 1;
  }));
  const max = Math.max(0, ...matrix.cohortes.flatMap((c) => c.valores.filter((v) => v !== null)));
  return (
    <div className="table-wrap">
      <table className="table table-compact matrix">
        <thead>
          <tr>
            <th className="sticky-col">Cohorte</th>
            <th className="num">Primíparos</th>
            {Array.from({ length: cols }, (_, i) => <th key={i} className="num">S{i + 1}</th>)}
          </tr>
        </thead>
        <tbody>
          {matrix.cohortes.map((c) => {
            const k = selected.indexOf(c.cohorte);
            return (
              <tr key={c.cohorte}>
                <td className="sticky-col">
                  <label className="cohort-check" title="Mostrar en la gráfica">
                    <input type="checkbox" checked={k >= 0} onChange={() => onToggle(c.cohorte)} />
                    {k >= 0 && <span className="swatch" style={{ background: SERIES_COLORS[k] }} />}
                    <strong>{c.cohorte}</strong>
                  </label>
                </td>
                <td className="num">{fmtNum(c.primiparos)}</td>
                {Array.from({ length: cols }, (_, i) => (
                  <td key={i} className="num" style={heat(c.valores[i], max)}>{c.valores[i] === null || c.valores[i] === undefined ? '' : fmtPct(c.valores[i], 1)}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function defaultCohorts(matrix) {
  const withData = matrix.cohortes.filter((c) => c.valores.filter((v) => v !== null).length >= 2).map((c) => c.cohorte);
  const firsts = withData.filter((c) => c.endsWith('-1'));
  const pool = firsts.length >= 3 ? firsts : withData;
  return pool.slice(-Math.min(6, MAX_COHORTS));
}

export default function IndicatorsView() {
  const notify = useToast();
  const [nivel, setNivel] = useState('pregrado');
  const [vista, setVista] = useState('ies');
  const [programas, setProgramas] = useState([]);
  const [tab, setTab] = useState('TDA');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cohortSel, setCohortSel] = useState({ TDC: [], TGA: [] });
  const [downloading, setDownloading] = useState(false);

  const params = useMemo(() => qs({ nivel, vista, programas: programas.join('|') }), [nivel, vista, programas]);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    setError('');
    api.get(`/indicators${params}`)
      .then((d) => {
        if (!alive) return;
        setData(d);
        setCohortSel({ TDC: defaultCohorts(d.tdc), TGA: defaultCohorts(d.tga_cohortes) });
      })
      .catch((e) => alive && setError(e.message))
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [params]);

  const changeNivel = (n) => { setNivel(n); setProgramas([]); };

  const download = async () => {
    setDownloading(true);
    try {
      await api.download(`/indicators/export${params}`, 'Indicadores_SPADIES.xlsx');
    } catch (e) {
      notify(e.message, 'error');
    } finally {
      setDownloading(false);
    }
  };

  const toggleCohort = (key, cohorte) => setCohortSel((s) => {
    const cur = s[key];
    if (cur.includes(cohorte)) return { ...s, [key]: cur.filter((c) => c !== cohorte) };
    if (cur.length >= MAX_COHORTS) { notify(`Máximo ${MAX_COHORTS} cohortes en la gráfica.`, 'warning', 3000); return s; }
    return { ...s, [key]: [...cur, cohorte] };
  });

  const meta = INDICATORS[tab];
  const hasData = data && data.periodos.length > 0;

  const cohortChart = (matrix, key) => {
    const chosen = cohortSel[key].map((c) => matrix.cohortes.find((x) => x.cohorte === c)).filter(Boolean);
    const len = Math.max(0, ...chosen.map((c) => c.valores.map((v, i) => (v !== null ? i + 1 : 0)).reduce((a, b) => Math.max(a, b), 0)));
    return {
      categories: Array.from({ length: len }, (_, i) => `S${i + 1}`),
      series: chosen.map((c) => ({ name: c.cohorte, values: c.valores.slice(0, len) })),
    };
  };

  const renderTab = () => {
    if (!hasData) return null;
    switch (tab) {
      case 'TDA':
      case 'TAI': {
        const rows = tab === 'TDA' ? data.tda : data.tai;
        return (
          <>
            <LineChart ariaLabel={`${meta.title} por periodo`} categories={rows.map((r) => r.periodo)}
              series={[{ name: meta.title, values: rows.map((r) => r.tasa) }]} xLabel="Periodo" />
            <PeriodTable rows={rows} countKey={tab === 'TDA' ? 'desertores' : 'ausentes'} countLabel={tab === 'TDA' ? 'Desertores' : 'Ausentes'} />
          </>
        );
      }
      case 'TDC':
      case 'TGA': {
        const matrix = tab === 'TDC' ? data.tdc : data.tga_cohortes;
        const ch = cohortChart(matrix, tab);
        const agg = tab === 'TDC' ? data.tdpa : data.tga;
        return (
          <>
            {tab === 'TGA' && (
              <>
                <h4 className="section-title">Graduación acumulada (todas las cohortes)</h4>
                <LineChart ariaLabel="Tasa de graduación acumulada" categories={agg.map((r) => `S${r.semestre}`)}
                  series={[{ name: 'TGA', values: agg.map((r) => r.tasa) }]} xLabel="Semestre" />
                <SemesterTable rows={agg} countKey="graduados" countLabel="Graduados" />
                <h4 className="section-title">Graduación por cohorte</h4>
              </>
            )}
            {matrix.cohortes.length === 0 ? (
              <Empty>No hay cohortes: cargue los archivos de Matriculados Nuevos.</Empty>
            ) : (
              <>
                <p className="muted small">Marque las cohortes que desea ver en la gráfica (máximo {MAX_COHORTS}).</p>
                {ch.series.length > 0
                  ? <LineChart ariaLabel={`${meta.title} por cohorte`} categories={ch.categories} series={ch.series} xLabel="Semestre de trayectoria" />
                  : <Empty>Seleccione al menos una cohorte en la tabla.</Empty>}
                <CohortMatrix matrix={matrix} selected={cohortSel[tab]} onToggle={(c) => toggleCohort(tab, c)} />
              </>
            )}
          </>
        );
      }
      case 'TDPA':
        return (
          <>
            <LineChart ariaLabel="Tasa de deserción promedio acumulada" categories={data.tdpa.map((r) => `S${r.semestre}`)}
              series={[{ name: 'TDPA', values: data.tdpa.map((r) => r.tasa) }]} xLabel="Semestre" />
            <SemesterTable rows={data.tdpa} countKey="desertores" countLabel="Desertores" />
          </>
        );
      default:
        return null;
    }
  };

  const tda = lastWith(data?.tda);
  const tai = lastWith(data?.tai);
  const tdpa = lastWith(data?.tdpa, 3);   // semestre más alto con al menos 3 cohortes
  const tga = lastWith(data?.tga, 3);
  const lastCount = data?.conteos?.[data.conteos.length - 1];

  return (
    <div>
      <PageHeader
        title="Indicadores de deserción y permanencia"
        subtitle="Metodología SPADIES 3.0 · cifras validadas contra las publicadas por el Ministerio para la UCO."
        actions={<button className="btn btn-primary" onClick={download} disabled={!hasData || downloading}>{downloading ? 'Generando…' : '⬇ Descargar Excel'}</button>}
      />

      <Card className="filters">
        <div className="filter-row">
          <div className="filter">
            <span className="field-label">Nivel de formación</span>
            <Segmented options={NIVELES} value={nivel} onChange={changeNivel} ariaLabel="Nivel de formación" />
          </div>
          <div className="filter">
            <span className="field-label">Tipo de cálculo</span>
            <Segmented options={VISTAS} value={vista} onChange={setVista} ariaLabel="Tipo de cálculo" />
          </div>
          <div className="filter filter-grow">
            <span className="field-label">Programas</span>
            <ProgramPicker nivel={nivel} value={programas} onChange={setProgramas} />
          </div>
        </div>
        <p className="muted small">{VISTAS.find((v) => v.id === vista).help}
          {nivel !== 'pregrado' && ' SPADIES solo publica pregrado: las cifras de posgrado usan la misma metodología pero no tienen referencia oficial.'}</p>
      </Card>

      {error && <Alert type="error">{error}</Alert>}
      {loading && !data && <Spinner label="Calculando indicadores…" />}

      {data && !hasData && !loading && (
        <Empty>No hay información cargada para este filtro. Un administrador debe cargar los archivos en "Carga de información".</Empty>
      )}

      {hasData && (
        <>
          {data.ventana && (
            <p className="muted small window-note">
              Ventana de análisis: <strong>{data.ventana.desde} a {data.ventana.hasta}</strong> ({data.ventana.periodos} periodos).
              Se muestran como máximo los últimos {data.ventana.max_periodos / 2} años ({data.ventana.max_periodos} periodos) y hasta {data.ventana.max_semestres} semestres de trayectoria.
            </p>
          )}

          {data.advertencias?.length > 0 && (
            <details className="alert alert-warning">
              <summary><strong>Advertencias de datos ({data.advertencias.length})</strong>: hay archivos faltantes que afectan algunos indicadores.</summary>
              <ul>{data.advertencias.map((w) => <li key={w}>{w}</li>)}</ul>
            </details>
          )}

          <div className={`kpis ${loading ? 'is-loading' : ''}`}>
            <Kpi label="Deserción anual (TDA)" value={fmtPct(tda?.tasa)} detail={tda ? `Periodo ${tda.periodo}` : 'Sin dato'} />
            <Kpi label="Ausencia intersemestral (TAI)" value={fmtPct(tai?.tasa)} detail={tai ? `Base ${tai.periodo}` : 'Sin dato'} />
            <Kpi label="Deserción acumulada (TDPA)" value={fmtPct(tdpa?.tasa)} detail={tdpa ? `Al semestre ${tdpa.semestre} (${tdpa.cohortes} cohortes)` : 'Sin dato'} />
            <Kpi label="Graduación acumulada (TGA)" value={fmtPct(tga?.tasa)} detail={tga ? `Al semestre ${tga.semestre} (${tga.cohortes} cohortes)` : 'Sin dato'} />
            <Kpi label="Matriculados" value={fmtNum(lastCount?.matriculados)} detail={lastCount ? `Periodo ${lastCount.periodo}` : ''} />
          </div>

          <div className="tabs" role="tablist">
            {INDICATOR_ORDER.map((k) => (
              <button key={k} role="tab" aria-selected={tab === k} className={tab === k ? 'active' : ''} onClick={() => setTab(k)}>
                <strong>{k}</strong><span className="tab-sub">{INDICATORS[k].title}</span>
              </button>
            ))}
          </div>

          <Card className={loading ? 'is-loading' : ''}>
            <div className="indicator-head">
              <div>
                <h3>{meta.title} ({tab})</h3>
                <p>{meta.description}</p>
              </div>
              <Formula meta={meta} />
            </div>
            {renderTab()}
            <p className="muted small note">ℹ️ {meta.note}</p>
          </Card>
        </>
      )}
    </div>
  );
}
