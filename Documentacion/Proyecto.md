# FICHA PROYECTO: DEFC.004.00 (2018-07-19)
**Universidad Católica de Oriente — Dirección de Extensión y Proyección Social**

## Información General
* **Título del Proyecto:** Sistema para el análisis de la deserción en la Universidad Católica de Oriente
* **Convenio / Contrato:** Contrato de práctica social
* **Duración:** 5 meses
* **Localización:** Universidad Católica de Oriente – Rionegro (Antioquia)
* **Objetivos de Desarrollo Sostenible (ODS):**
  * 4. Educación de calidad
  * 10. Reducción de las desigualdades

## Equipo de Trabajo
* **Funcionarios Responsables:**
  * Sandra Marcela Henao Raigoza — Asistente Académica
  * Luz Mery Ríos Alzate — Coordinadora Ingeniería de Sistemas
* **Estudiantes Participantes:**
  * John Jairo Duque Zuluaga (Ingeniería de Sistemas)

## Población Beneficiaria
* **Beneficiarios Directos:**
  * Dirección de docencia
  * Decanos y Coordinadores
* **Beneficiarios Indirectos:**
  * Dirección Académica - UCO
  * Decanos - UCO
  * Coordinadores - UCO
  * Docentes - UCO
  * Estudiantes - UCO

## Recursos Necesarios
* Persona para la programación de software
* Computador
* Escritorio
* Pantalla auxiliar

## Planteamiento del Proyecto
* **Problema a Resolver:** Carencia de herramientas analíticas y estadísticas que permitan a la Universidad Católica de Oriente realizar un seguimiento efectivo de la deserción y retención estudiantil, limitando la capacidad de implementar políticas educativas eficaces. Se requiere un software para recoger, analizar y visualizar datos eficientemente.
* **Justificación:** Proporcionar herramientas tecnológicas y analíticas para la toma de decisiones informadas basadas en datos sobre deserción y retención estudiantil, apoyando la planificación organizacional y la predicción/prevención de futuros casos.
* **Objetivo General:** Desarrollar un software estadístico y analítico que permita a la Universidad Católica de Oriente realizar un seguimiento y mejorar las estrategias de prevención de la deserción y de la retención estudiantil.
* **Objetivos Específicos:**
  1. Identificar las variables clave para el seguimiento de la deserción y retención estudiantil.
  2. Diseñar y desarrollar un software que permita la recolección, análisis y visualización de estas variables.

## Plan de Trabajo y Productos Esperados

| Actividad | Entregable / Producto Esperado |
| :--- | :--- |
| **Estudio del sistema** | Documentación de requisitos |
| **Diseño Arquitectónico** | Documentación de arquitectura |
| **Desarrollo de software** | Código |
| **Implementación** | Aplicación web expuesta |
| **Pruebas** | Resultado de los indicadores |

## Indicadores de Resultado
* Tasa de deserción anual
* Tasa de deserción por cohorte
* Tasa de deserción promedio acumulada
* Tasa de graduación acumulada
* Tasa de ausencia intersemestral

## Aspectos Éticos e Impacto
* **Aspectos Éticos:** Manejo de información sensible.
* **Impacto Social y Curricular:** Fortalecimiento de la relación entre la enseñanza y la investigación para la formación del estudiante.

## Referencias Bibliográficas
* Ministerio de Educación Nacional (2018). *El Ministerio de Educación Nacional presenta la nueva versión del Sistema para la Prevención y Análisis de la Deserción en las Instituciones de Educación Superior - SPADIES 3.0*. [Archivo PDF]. https://www.mineducacion.gov.co/sistemasinfo/spadies/
```[cite: 1]

---

### Documento 2: `PROYECTO DE PRÁCTICA.docx`

```markdown
# PROYECTO DE PRÁCTICA: Sistema Analítico de Deserción UCO

## Descripción del Proyecto
Sistema solicitado por la Dirección Académica de la UCO para el análisis de la deserción en niveles de **pregrado y postgrado**, procesando información semestral para consultas analíticas por facultad y por programa.

## Entidades y Estados
* **Definición de Estudiante:** Estudiante de primer curso.
* **Niveles de Formación:** Pregrado, Postgrado.
* **Estados del Estudiante:** Desertor, Graduado, Primíparo, Ausente, Matriculado.
* **Origen de Datos:** Base de datos Oracle de la UCO.

## Requerimientos del Sistema
* **Gestión de Usuarios:** Rol de Administrador para configurar múltiples accesos con usuario y contraseña.
* **Módulo de Analítica:** 
  * Acceso mediante menú `Consultas` > submenú `Analíticas` (Roles: Administrador y Analista).
  * Filtros mediante listas desplegables: Tipo de consulta (indicador), Nivel de formación, Facultad (*específica o todas*), Programa (*específico o todos*).
  * Botón de acción: `Generar consulta`.
  * Visualización de datos en formato de tabla de resultados.

## Fórmulas de Indicadores Analíticos

### 1. Tasa de Deserción Anual ($TDA$)
Mide el comportamiento de la deserción en el corto plazo respecto a dos periodos atrás ($t-2$).

$$TDA_t = \left( \frac{\text{Desertores}_t}{\text{Matriculados}_{t-2}} \right) \times 100$$

*Donde $t$ es el período.*

---

### 2. Tasa de Deserción por Cohorte ($TDC$)
Comportamiento de la deserción para una cohorte específica acumulada hasta un semestre.

$$TDC_{c,s} = \left( \frac{\sum_{s=1}^S \text{Desertores}_{c,s}}{\text{Primíparos}_c} \right) \times 100$$

*Donde $c$ es la cohorte y $s$ el semestre.*

---

### 3. Tasa de Deserción Promedio Acumulada ($TDPA$)
Tendencia estructural de largo plazo considerando el total acumulado de todas las cohortes.

$$TDPA_s = \left( \frac{\sum_{c=1}^C \sum_{s=1}^S \text{Desertores}_{c,s}}{\sum_{c=1}^C \text{Primíparos}_c} \right) \times 100$$

*Donde $c$ es la cohorte y $s$ el semestre.*

---

### 4. Tasa de Graduación Acumulada ($TGA$)
Porcentaje acumulado de graduados sobre el total de primíparos de todas las cohortes.

$$TGA_s = \left( \frac{\sum_{c=1}^C \sum_{s=1}^S \text{Graduados}_{c,s}}{\sum_{c=1}^C \text{Primíparos}_c} \right) \times 100$$

*Donde $c$ es la cohorte y $s$ el semestre.*

---

### 5. Tasa de Ausencia Intersemestral ($TAI$)
Proporción de estudiantes matriculados en el periodo anterior ($t-1$) en estado ausente en el periodo actual.

$$TAI_t = \left( \frac{\text{Ausentes}_t}{\text{Matriculados}_{t-1}} \right) \times 100$$

*Donde $t$ es el período.*

---

### 6. Tasa de Supervivencia
Proporción de estudiantes en cada semestre que permanecen matriculados luego de haber sido primíparos de un programa académico en una IES.
```[cite: 2, 3]

---

### Documento 3: `MANUAL SPADIES.pdf`

```markdown
# SPADIES 3.0: Sistema para la Prevención y Análisis de la Deserción en las Instituciones de Educación Superior
**Ministerio de Educación Nacional (MEN)**

## Antecedentes y Evolución
* El sistema SPADIES consolida datos desde 1998 para el seguimiento de la deserción, condiciones socioeconómicas e indicadores de permanencia en pregrado.
* En 2018 se lanza **SPADIES 3.0**, integrando directamente las bases del **SNIES** junto con fuentes de **ICETEX** e **ICFES** bajo administración del Ministerio de Educación Nacional (sucediendo al CEDE de la Universidad de los Andes).

## Metodología: Enfoque de Historia de Vida
Evalúa eventos y transiciones académicas semestre a semestre de cada estudiante para construir trayectorias y determinar tiempos de deserción.

### Estados del Estudiante en SPADIES 3.0
* **Desertor:** Estudiante que voluntaria o forzosamente no se matricula por dos (2) o más períodos consecutivos, sin registrar graduación ni retiro disciplinario.
* **Activo:** Estudiante matriculado en el periodo actual o anterior (incluye: *Primíparos*, *Matriculados regulares* y *Ausentes* con 1 semestre sin matrícula).
* **Graduado:** Individuo que culminó su ciclo académico y obtuvo el título.
* **Retirado:** Estudiante ausente de la IES por motivos disciplinarios.

## Tipos de Cálculo según Alcance de Movilidad

```smartdown/tabs
### Vista Programa
Estudiante que no se matricula en el mismo programa académico durante dos o más períodos consecutivos.

### Vista IES
Estudiante que no se matricula en la institución durante dos o más períodos consecutivos.

### Vista Sistema
Estudiante que no se matricula en ningún programa académico de ninguna IES a nivel nacional durante dos o más períodos consecutivos.