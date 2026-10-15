### 💡 Justificación
[cite_start]Proveer a la institución de un software analítico que centralice la recolección, procesamiento y visualización de variables clave[cite: 10, 11]. [cite_start]La herramienta facilitará la toma de decisiones informadas, mejorará la planificación académica y permitirá anticipar y prevenir casos futuros de abandono estudiantil[cite: 11, 12, 13].

---

## 3. Objetivos del Proyecto

### Objetivo General
[cite_start]Desarrollar un software estadístico y analítico que permita a la Universidad Católica de Oriente realizar un seguimiento continuo y optimizar las estrategias de prevención de la deserción y fomento de la retención estudiantil en niveles de pregrado y postgrado[cite: 16, 27].

### Objetivos Específicos
1. [cite_start]Identificar y parametrizar las variables clave para el seguimiento de la deserción y retención estudiantil según lineamientos institucionales y del MEN (SPADIES)[cite: 18, 23, 24].
2. [cite_start]Diseñar y construir el software que gestione la extracción, procesamiento analítico y visualización interactiva de dichas variables[cite: 10, 19].

---

## 4. Requerimientos Funcionales y de Arquitectura

- [ ] [cite_start]**Gestión de Accesos:** Módulo de administración para configuración y control de credenciales (Usuario/Contraseña) con soporte de roles (*Administrador*, *Analista*)[cite: 32, 33].
- [ ] [cite_start]**Módulo de Consultas y Analítica:** Navegación por menú `Consultas > Analíticas`[cite: 33].
- [ ] [cite_start]**Filtros Paramétricos:** Selector para Indicador, Nivel de Formación (*Pregrado/Postgrado*), Facultad (*Específica o Todas*) y Programa Académico (*Específico o Todos*)[cite: 27, 29, 33].
- [ ] [cite_start]**Visualización de Resultados:** Procesamiento mediante botón `Generar Consulta` y renderizado de resultados en tablas y reportes analíticos[cite: 33, 34].
- [ ] [cite_start]**Integración de Datos:** Conexión y consulta sobre el repositorio central Oracle UCO[cite: 35].
- [ ] [cite_start]**Aspectos Éticos:** Protocolos y control de seguridad para el manejo de información institucional sensible[cite: 22].

---

## 5. Glosario y Definiciones de Estado (Metodología SPADIES)

### Estado: Desertor
[cite_start]Estudiante que de manera voluntaria o forzosa no se observa como matriculado por dos (2) o más períodos académicos consecutivos, sin haber registrado graduación o retiro por causas disciplinarias[cite: 2, 56].

### Estado: Activo / Matriculado
[cite_start]Estudiante que se encuentra matriculado o que estuvo matriculado en el semestre inmediatamente anterior en un programa académico[cite: 3, 58]. Incluye a:
* [cite_start]**Primíparo / Primer Curso:** Estudiante matriculado por primera vez en un programa[cite: 28, 53].
* [cite_start]**Ausente:** Estudiante que lleva exactamente un semestre sin matricularse (alto riesgo de deserción)[cite: 53].

### Estado: Graduado
[cite_start]Individuo que ha culminado satisfactoriamente su plan de estudios y ha obtenido el título académico correspondiente[cite: 4, 60].

### Estado: Retirado
[cite_start]Estudiante que se desvincula de la institución por sanciones o motivos estrictamente disciplinarios (no académicos)[cite: 4, 62].

---

## 6. Fórmulas e Indicadores Analíticos

### 1. Tasa de Deserción Anual ($TDA$)
[cite_start]Mide el comportamiento de la deserción en el corto plazo (respecto a dos periodos atrás)[cite: 5, 92]:

[cite_start]$$TDA_{t} = \left( \frac{\text{Desertores}_{t}}{\text{Matriculados}_{t-2}} \right) \times 100$$ [cite: 92]

### 2. Tasa de Deserción por Cohorte ($TDC$)
[cite_start]Analiza el fenómeno de abandono en estudiantes que iniciaron en el mismo periodo[cite: 92]:

[cite_start]$$TDC_{c,s} = \left( \frac{\sum_{s=1}^{S} \text{Desertores}_{c,s}}{\text{Primíparos}_{c}} \right) \times 100$$ [cite: 92]

[cite_start]*(Donde $c$ es la cohorte y $s$ el semestre de corte)[cite: 92].*

### 3. Tasa de Deserción Promedio Acumulada ($TDPA$)
[cite_start]Refleja la tendencia estructural a largo plazo considerando todas las cohortes históricas[cite: 92]:

[cite_start]$$TDPA_{s} = \left( \frac{\sum_{c=1}^{C}\sum_{s=1}^{S} \text{Desertores}_{c,s}}{\sum_{c=1}^{C} \text{Primíparos}_{c}} \right) \times 100$$ [cite: 92]

### 4. Tasa de Graduación Acumulada ($TGA$)
[cite_start]Porcentaje acumulado de estudiantes titulados respecto al ingreso histórico[cite: 6, 92]:

[cite_start]$$TGA_{s} = \left( \frac{\sum_{c=1}^{C}\sum_{s=1}^{S} \text{Graduados}_{c,s}}{\sum_{c=1}^{C} \text{Primíparos}_{c}} \right) \times 100$$ [cite: 92]

### 5. Tasa de Ausencia Intersemestral ($TAI$)
[cite_start]Proporción de estudiantes que se encontraban activos un semestre atrás y entran en estado ausente[cite: 92]:

[cite_start]$$TAI_{t} = \left( \frac{\text{Ausentes}_{t}}{\text{Matriculados}_{t-1}} \right) \times 100$$ [cite: 92]

### 6. Tasa de Supervivencia ($TS$)
[cite_start]Proporción de estudiantes que se mantienen matriculados tras su ingreso[cite: 92]:

[cite_start]$$TS_{s} = \left( \frac{\text{Matriculados}_{s}}{\sum_{c=1}^{C} \text{Primíparos}_{c}} \right) \times 100$$ [cite: 93]

---

## 7. Plan de Trabajo y Cronograma (5 Meses)

| Actividad | M1 | M2 | M3 | M4 | M5 | Entregable / Producto Esperado |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Estudio del Sistema** | **X** | | | | | [cite_start]Documentación de requisitos [cite: 21] |
| **Diseño Arquitectónico** | | **X** | | | | [cite_start]Documentación de arquitectura [cite: 21] |
| **Desarrollo de Software** | | | **X** | **X** | **X** | [cite_start]Código [cite: 21] |
| **Implementación** | | | | | **X** | [cite_start]Aplicación web expuesta [cite: 21] |
| **Pruebas y Validación** | | | | | **X** | [cite_start]Resultado de los indicadores [cite: 21] |

---

## 8. Referencias

* Ministerio de Educación Nacional (2018). *El Ministerio de Educación Nacional presenta la nueva versión del Sistema para la Prevención y Análisis de la Deserción en las Instituciones de Educación Superior - SPADIES 3.0*. [cite_start]Bogotá D.C.: MEN[cite: 23, 24].