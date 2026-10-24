// Definiciones de los 5 indicadores (metodología SPADIES 3.0, reglas validadas contra cifras oficiales).
export const INDICATORS = {
  TDA: {
    title: 'Tasa de Deserción Anual',
    symbol: 'TDA', sub: 't',
    num: 'Desertores en t', den: 'Matriculados en t − 2',
    description: 'Mide la deserción de corto plazo: de los estudiantes matriculados hace un año (t − 2), qué porcentaje lleva dos periodos consecutivos sin matrícula (t − 1 y t) y no se ha graduado.',
    note: 'El periodo de la etiqueta es t. Los primeros dos periodos cargados no tienen t − 2 de referencia.',
  },
  TAI: {
    title: 'Tasa de Ausencia Intersemestral',
    symbol: 'TAI', sub: 't',
    num: 'Ausentes en t + 1', den: 'Matriculados en t',
    description: 'Alerta temprana: de los matriculados en el periodo t, qué porcentaje no renueva matrícula en el periodo siguiente (sin haberse graduado).',
    note: 'Igual que SPADIES, la etiqueta es el periodo base t. El último periodo cargado queda sin dato hasta cargar el siguiente.',
  },
  TDC: {
    title: 'Tasa de Deserción por Cohorte',
    symbol: 'TDC', sub: 'c, s',
    num: 'Σ desertores de la cohorte c hasta s', den: 'Primíparos de la cohorte c',
    description: 'Seguimiento de cada cohorte de primíparos: porcentaje acumulado que abandonó (no volvió a matricularse ni se graduó), asignado al semestre de su última matrícula.',
    note: 'La deserción se confirma con dos periodos sin matrícula, por eso los dos últimos semestres de cada cohorte quedan pendientes. Las cifras de cohortes recientes se actualizan al cargar nuevos periodos.',
  },
  TDPA: {
    title: 'Tasa de Deserción Promedio Acumulada',
    symbol: 'TDPA', sub: 's',
    num: 'Σc Σs desertores', den: 'Σc primíparos',
    description: 'Tendencia estructural: deserción acumulada al semestre s considerando todas las cohortes que ya alcanzaron ese semestre.',
    note: 'Cada semestre agrega solo las cohortes que lo alcanzan; la columna "Cohortes" indica cuántas.',
  },
  TGA: {
    title: 'Tasa de Graduación Acumulada',
    symbol: 'TGA', sub: 's',
    num: 'Σc Σs graduados', den: 'Σc primíparos',
    description: 'Porcentaje acumulado de primíparos que obtienen el título hasta el semestre s, sumando todas las cohortes que alcanzan ese semestre.',
    note: 'Requiere cargar los archivos de egresados. La graduación se ubica en el semestre según el mes de la fecha de grado.',
  },
};

export const INDICATOR_ORDER = ['TDA', 'TAI', 'TDC', 'TDPA', 'TGA'];
