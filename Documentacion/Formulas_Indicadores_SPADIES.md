# Fórmulas y reglas de cálculo de los indicadores (SPADIES 3.0 · UCO)

Este documento describe exactamente cómo calcula UCO Analytics cada indicador. Las reglas se validaron contra las
exportaciones oficiales de SPADIES para la UCO (pregrado, 2018-1 a 2024-2) y reproducen sus cifras con un error medio
menor a 1 punto porcentual. La prueba automática `backend/tests/test_spadies_validation.py` verifica esta
coincidencia.

## Insumos

| Archivo | Uso |
|---|---|
| Matriculados (por semestre) | Población matriculada de cada periodo. |
| Matriculados nuevos (por semestre) | **Primíparos**: definen la cohorte de ingreso. |
| Egresados (por semestre o por año) | Graduados. El semestre se toma del **mes de la fecha de grado** (enero–junio = 1, julio–diciembre = 2). |

Periodos en formato `AAAA-S`, en serie consecutiva.

## Nivel de formación y tipo de cálculo

- **Nivel**: pregrado, posgrado o ambos, según el nivel de cada programa en el Catálogo de programas. SPADIES solo
  publica pregrado; posgrado usa las mismas reglas sin referencia oficial.
- **Tipo de cálculo** (igual que SPADIES 3.0):
  - **Institución (IES)**: el estudiante se identifica por su documento. Cambiar de programa dentro de la UCO no es
    deserción.
  - **Programa**: el estudiante se identifica por documento + programa. Salir del programa es deserción del programa,
    aunque continúe en otro.
- **Filtro de programas**: limita la población (matriculados base, cohortes y graduados) a los programas elegidos.
  En la vista IES, la ausencia se evalúa en toda la institución.

## Ventana de análisis (requisito institucional)

- Cada indicador se reporta para los **últimos 10 años**: los últimos **20 periodos** cargados (TDA y TAI por periodo; TDC y TGA por cohorte).
- Los indicadores por semestre de trayectoria (TDC, TDPA, TGA) muestran como máximo **20 semestres** (S1 a S20).
- TDPA y TGA agregan solo las cohortes que están dentro de la ventana.
- Los cálculos usan toda la información cargada (por ejemplo, para saber si un estudiante del primer periodo de la ventana estaba matriculado dos periodos antes); la ventana solo limita lo que se reporta.

## Estados SPADIES

- **Activo**: matriculado en el periodo o en el periodo anterior.
- **Desertor**: no se observa matriculado durante dos o más periodos consecutivos y no registra grado.
- **Graduado**: obtuvo el título.
- *Retirado (motivos disciplinarios)*: no se calcula porque los archivos institucionales no traen esa información.

## 1. Tasa de Deserción Anual (TDA)

$$TDA_t = \frac{\text{Desertores en } t}{\text{Matriculados en } t-2} \times 100$$

- Denominador: **todos** los matriculados en *t − 2* (definición SPADIES 3.0).
- Desertores en *t*: matriculados en *t − 2* **sin matrícula en t − 1 ni en t** y sin grado hasta *t*.

## 2. Tasa de Ausencia Intersemestral (TAI)

$$TAI_t = \frac{\text{Ausentes en } t+1}{\text{Matriculados en } t} \times 100$$

- La etiqueta es el **periodo base** *t* (convención de SPADIES). El último periodo cargado queda sin dato.
- Ausentes: matriculados en *t* que no se matriculan en *t + 1* y no se han graduado.

## 3. Tasa de Deserción por Cohorte (TDC)

$$TDC_{c,s} = \frac{\sum_{s'=1}^{s} \text{Desertores}_{c,s'}}{\text{Primíparos}_c} \times 100$$

- Primíparos de la cohorte *c*: archivo de Matriculados nuevos de *c*.
- Un primíparo es **desertor** si **no vuelve a matricularse y nunca se gradúa** con la información disponible.
- La deserción se **asigna al semestre de su última matrícula** y se acumula. Por eso SPADIES ya muestra deserción en S1
  (estudiantes que solo cursaron el primer semestre).
- Se requieren dos periodos posteriores observados para confirmar la deserción: los dos últimos semestres de cada
  cohorte quedan pendientes y las cifras recientes se actualizan al cargar nuevos periodos (igual que en SPADIES).

## 4. Tasa de Deserción Promedio Acumulada (TDPA)

$$TDPA_s = \frac{\sum_{c} \sum_{s'=1}^{s} \text{Desertores}_{c,s'}}{\sum_{c} \text{Primíparos}_c} \times 100$$

Suma sobre las cohortes que ya alcanzaron el semestre *s*.

## 5. Tasa de Graduación Acumulada (TGA)

$$TGA_s = \frac{\sum_{c} \text{Graduados}_{c,\le s}}{\sum_{c} \text{Primíparos}_c} \times 100$$

Graduados de cada cohorte hasta el semestre *s*, sumando las cohortes que alcanzan *s*.

> SPADIES calcula TDPA y TGA con todas las cohortes desde 1998. La aplicación usa las cohortes cargadas; para
> igualar esas dos cifras exactamente se debe cargar la misma historia.

## Validación (pregrado, 2018-1 a 2024-2)

| Indicador | Vista IES | Vista Programa |
|---|---|---|
| TDA | 0,34 pp | 0,33 pp |
| TAI | 0,42 pp | 0,41 pp |
| TDC | 0,95 pp | 0,89 pp |

Fuera de alcance por decisión del proyecto: tasa de supervivencia y tasa de deserción periodo 2.8.
