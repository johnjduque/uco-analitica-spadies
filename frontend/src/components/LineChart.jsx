import { useMemo, useRef, useState } from 'react';

// Paleta categórica validada (orden fijo, nunca se recicla). Ver skill dataviz.
export const SERIES_COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948'];

const W = 820;
const PAD = { top: 16, right: 18, bottom: 44, left: 52 };

function niceMax(v) {
  if (!v || v <= 0) return 10;
  const exp = 10 ** Math.floor(Math.log10(v));
  const n = v / exp;
  const step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10;
  return step * exp;
}

/**
 * Gráfica de líneas en SVG, sin dependencias.
 * series: [{ name, values: [number|null], color? }]
 * categories: etiquetas del eje X (misma longitud que values)
 */
export default function LineChart({ series, categories, height = 250, yLabel = '%', xLabel, format = (v) => `${v.toFixed(2)}%`, ariaLabel }) {
  const [hidden, setHidden] = useState(() => new Set());
  const [hover, setHover] = useState(null);
  const svgRef = useRef(null);

  const visible = series.filter((s) => !hidden.has(s.name));
  const maxY = useMemo(() => {
    const vals = visible.flatMap((s) => s.values.filter((v) => v !== null && v !== undefined));
    return niceMax(Math.max(0, ...vals) * 1.08);
  }, [visible]);

  const innerW = W - PAD.left - PAD.right;
  const innerH = height - PAD.top - PAD.bottom;
  const n = categories.length;
  const x = (i) => PAD.left + (n <= 1 ? innerW / 2 : (i * innerW) / (n - 1));
  const y = (v) => PAD.top + innerH - (v / maxY) * innerH;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => t * maxY);
  const labelEvery = Math.max(1, Math.ceil(n / 14));

  const pathFor = (values) => {
    let d = '';
    let pen = false;
    values.forEach((v, i) => {
      if (v === null || v === undefined) { pen = false; return; }
      d += `${pen ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`;
      pen = true;
    });
    return d;
  };

  const onMove = (e) => {
    const rect = svgRef.current.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * W;
    if (px < PAD.left - 10 || px > W - PAD.right + 10 || n === 0) { setHover(null); return; }
    const i = n <= 1 ? 0 : Math.round(((px - PAD.left) / innerW) * (n - 1));
    setHover(Math.max(0, Math.min(n - 1, i)));
  };

  const toggle = (name) => {
    const next = new Set(hidden);
    if (next.has(name)) next.delete(name); else next.add(name);
    if (next.size < series.length) setHidden(next);
  };

  if (!n) return <div className="empty">Sin datos para graficar.</div>;

  const tipItems = hover === null ? [] : visible
    .map((s) => ({ s, v: s.values[hover] }))
    .filter((t) => t.v !== null && t.v !== undefined);
  const tipLeft = hover === null ? 0 : (x(hover) / W) * 100;

  return (
    <div className="chart">
      <div className="chart-plot">
        <svg ref={svgRef} viewBox={`0 0 ${W} ${height}`} role="img" aria-label={ariaLabel || 'Gráfica'}
          onMouseMove={onMove} onMouseLeave={() => setHover(null)} style={{ width: '100%', height: 'auto' }}>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={PAD.left} x2={W - PAD.right} y1={y(t)} y2={y(t)} className="grid" />
              <text x={PAD.left - 8} y={y(t) + 4} className="axis" textAnchor="end">{`${Math.round(t * 10) / 10}${yLabel}`}</text>
            </g>
          ))}
          {categories.map((c, i) => (i % labelEvery === 0 || i === n - 1) && (
            <text key={c} x={x(i)} y={height - PAD.bottom + 18} className="axis" textAnchor="middle">{c}</text>
          ))}
          {xLabel && <text x={PAD.left + innerW / 2} y={height - 6} className="axis axis-title" textAnchor="middle">{xLabel}</text>}
          {hover !== null && <line x1={x(hover)} x2={x(hover)} y1={PAD.top} y2={PAD.top + innerH} className="crosshair" />}
          {series.map((s, k) => !hidden.has(s.name) && (
            <path key={s.name} d={pathFor(s.values)} fill="none" stroke={s.color || SERIES_COLORS[k % SERIES_COLORS.length]}
              strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
          ))}
          {hover !== null && series.map((s, k) => {
            const v = s.values[hover];
            if (hidden.has(s.name) || v === null || v === undefined) return null;
            return <circle key={s.name} cx={x(hover)} cy={y(v)} r="4.5" fill={s.color || SERIES_COLORS[k % SERIES_COLORS.length]}
              stroke="#fff" strokeWidth="2" vectorEffect="non-scaling-stroke" />;
          })}
        </svg>
        {hover !== null && tipItems.length > 0 && (
          <div className="chart-tip" style={{ left: `${tipLeft}%`, transform: `translateX(${tipLeft > 60 ? '-105%' : '8px'})` }}>
            <div className="chart-tip-title">{categories[hover]}</div>
            {tipItems.map(({ s, v }) => (
              <div key={s.name} className="chart-tip-row">
                <span className="swatch" style={{ background: s.color || SERIES_COLORS[series.indexOf(s) % SERIES_COLORS.length] }} />
                {series.length > 1 && <span>{s.name}</span>}
                <strong>{format(v)}</strong>
              </div>
            ))}
          </div>
        )}
      </div>
      {series.length > 1 && (
        <div className="chart-legend">
          {series.map((s, k) => (
            <button key={s.name} type="button" className={`legend-item ${hidden.has(s.name) ? 'off' : ''}`}
              onClick={() => toggle(s.name)} title="Mostrar u ocultar">
              <span className="swatch" style={{ background: s.color || SERIES_COLORS[k % SERIES_COLORS.length] }} />
              {s.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
