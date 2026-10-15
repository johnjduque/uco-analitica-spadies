# Fórmulas de Indicadores Analíticos de Deserción (SPADIES 3.0 - UCO)

Documentación técnica y matemática de las fórmulas estándar para el cálculo de indicadores de permanencia, deserción, ausencia y graduación en la **Universidad Católica de Oriente (UCO)**, basándose en la metodología **SPADIES 3.0 (Ministerio de Educación Nacional)**.

---

## 1. Tasa de Deserción Anual ($TDA_t$)

Mide el comportamiento de la deserción en el corto plazo respecto a dos periodos académicos atrás ($t-2$). Evalúa cuántos estudiantes matriculados hace un año cayeron en estado de deserción en el periodo evaluado.

### Fórmulas Matemática
$$TDA_t = \frac{\text{Desertores de } t}{\text{Matriculados en } t - 2} \times 100$$

### Definición de Variables:
* **$t$**: Periodo académico evaluado (ej. 2024-1).
* **$\text{Desertores de } t$**: Estudiantes matriculados en $t-2$ que no registraron matrícula ni en $t-1$ ni en $t$, y que no han obtenido el título de graduación.
* **$\text{Matriculados en } t - 2$**: Total de estudiantes matriculados en la institución o programa dos periodos atrás (un año antes).

---

## 2. Tasa de Deserción por Cohorte ($TDC_{c,s}$)

Mide el porcentaje acumulado de estudiantes desertores de una cohorte específica de ingreso ($c$) hasta un semestre determinado de su trayectoria ($s$), respecto al tamaño inicial de la cohorte (primíparos).

### Fórmula Matemática
$$TDC_{c,s} = \frac{\sum_{s=1}^{S} \text{Desertores}_{c,s}}{\text{Primíparos}_c} \times 100$$

### Definición de Variables:
* **$c$**: Cohorte de ingreso de los estudiantes (semestre en el que ingresaron por primera vez como primíparos).
* **$s$**: Semestre de trayectoria académica evaluado ($s = 1, 2, \dots, S$).
* **$\sum_{s=1}^{S} \text{Desertores}_{c,s}$**: Suma acumulada de estudiantes pertenecientes a la cohorte $c$ que se han retirado/desertado entre el semestre 1 y el semestre $S$.
* **$\text{Primíparos}_c$**: Número total de estudiantes primíparos que ingresaron inicialmente en la cohorte $c$.

---

## 3. Tasa de Deserción Promedio Acumulada ($TDPA_s$)

Refleja la tendencia estructural e institucional de largo plazo de la deserción. Agrupa y promedia el comportamiento acumulado de deserción a lo largo de múltiples cohortes de ingreso ($c=1 \dots C$) hasta un semestre de trayectoria específico ($s$).

### Fórmula Matemática
$$TDPA_s = \frac{\sum_{c=1}^{C} \sum_{s=1}^{S} \text{Desertores}_{c,s}}{\sum_{c=1}^{C} \text{Primíparos}_c} \times 100$$

### Definición de Variables:
* **$c$**: Índice de la cohorte de ingreso ($c = 1, 2, \dots, C$).
* **$s$**: Semestre de trayectoria considerado.
* **$\sum_{c=1}^{C} \sum_{s=1}^{S} \text{Desertores}_{c,s}$**: Total acumulado de desertores en el semestre $s$ sumando todas las cohortes analizadas.
* **$\sum_{c=1}^{C} \text{Primíparos}_c$**: Suma total de estudiantes primíparos de todas las cohortes consideradas.

---

## 4. Tasa de Graduación Acumulada ($TGA_s$)

Mide la eficacia institucional para llevar a los estudiantes a la culminación exitosa de sus estudios. Representa la proporción acumulada de graduados sobre el total de primíparos en un semestre de trayectoria $s$, sumando todas las cohortes.

### Fórmula Matemática
$$TGA_s = \frac{\sum_{c=1}^{C} \sum_{s=1}^{S} \text{Graduados}_{c,s}}{\sum_{c=1}^{C} \text{Primíparos}_c} \times 100$$

### Definición de Variables:
* **$c$**: Índice de la cohorte de ingreso ($c = 1, 2, \dots, C$).
* **$s$**: Semestre de trayectoria alcanzado.
* **$\sum_{c=1}^{C} \sum_{s=1}^{S} \text{Graduados}_{c,s}$**: Total acumulado de estudiantes graduados en o antes del semestre $s$ para todas las cohortes $C$.
* **$\sum_{c=1}^{C} \text{Primíparos}_c$**: Suma total del número de primíparos iniciales en todas las cohortes evaluadas.

---

## 5. Tasa de Ausencia Intersemestral ($TAI_t$)

Evalúa la movilidad de corto plazo y el riesgo inminente de deserción. Mide la proporción de estudiantes que estuvieron matriculados en el periodo inmediatamente anterior ($t-1$) pero que no registraron matrícula en el periodo actual ($t$).

### Fórmula Matemática
$$TAI_t = \frac{\text{Ausentes}_t}{\text{Matriculados}_{t-1}} \times 100$$

### Definición de Variables:
* **$t$**: Periodo académico actual evaluado.
* **$\text{Ausentes}_t$**: Número de estudiantes que se matricularon en el periodo $t-1$ pero no renovaron matrícula en el periodo $t$ (y que no han sido reportados como graduados).
* **$\text{Matriculados}_{t-1}$**: Total de estudiantes matriculados en el periodo inmediatamente anterior.

---

## Resumen Comparativo de los 5 Indicadores


---

## Alcance de Filtros y Origen de Datos

De acuerdo con la información extraída de los archivos Excel de **Matriculados** y **Graduados** subidos secuencialmente por periodo, el sistema permite realizar la filtración de cualquiera de los 5 indicadores bajo dos enfoques principales:

1. **🏛️ Toda la Universidad (Visión Global UCO):**
   * Consolida la totalidad de estudiantes matriculados, primíparos, desertores y graduados de la universidad sin distinción de programa.
   * Permite evaluar la tasa de deserción, retención y graduación a nivel institucional global.

2. **🎓 Por Programa Académico Específico:**
   * Filtra y calcula el indicador exclusivamente para la población estudiantil asociada al programa seleccionado (ej: *Ingeniería de Sistemas*, *Ingeniería Industrial*, *Administración de Empresas*, etc.).
   * Posibilita la comparación inter-programas y el diagnóstico focalizado para la toma de decisiones docentes y coordinaciones académicas.
