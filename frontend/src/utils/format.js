export const fmtPct = (v, digits = 2) =>
  v === null || v === undefined || Number.isNaN(v) ? '—' : `${Number(v).toFixed(digits)}%`;

export const fmtNum = (v) =>
  v === null || v === undefined ? '—' : Number(v).toLocaleString('es-CO');

export const fmtDateTime = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' });
};

export const NIVELES = [
  { id: 'pregrado', label: 'Pregrado' },
  { id: 'posgrado', label: 'Posgrado' },
  { id: 'todos', label: 'Pregrado y posgrado' },
];

export const VISTAS = [
  { id: 'ies', label: 'Institución (IES)', help: 'Cambiar de programa dentro de la universidad no es deserción.' },
  { id: 'programa', label: 'Programa', help: 'Salir del programa cuenta como deserción del programa, aunque siga en otro.' },
];
