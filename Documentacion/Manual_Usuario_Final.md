# MANUAL DE USUARIO FINAL
## SISTEMA ANALÍTICO DE DESERCIÓN Y PERMANENCIA ESTUDIANTIL (UCO ANALYTICS)
### Universidad Católica de Oriente (UCO) — Metodología SPADIES 3.0 · Versión 3.0

---

## 1. INTRODUCCIÓN

### 1.1. ¿Qué es UCO Analytics?
UCO Analytics es una aplicación web que calcula los indicadores oficiales de deserción y permanencia de la metodología **SPADIES 3.0** a partir de los archivos institucionales de matriculados, matriculados nuevos y egresados. Sus cifras de pregrado coinciden con las publicadas por SPADIES para la UCO con un error medio menor a 1 punto porcentual.

### 1.2. ¿Para qué sirve?
* Consultar los 5 indicadores: **TDA**, **TAI**, **TDC**, **TDPA** y **TGA**.
* Filtrar por **nivel de formación** (pregrado, posgrado o ambos), **tipo de cálculo** (Institución o Programa) y **programas**.
* Ver **gráficas** de cada indicador y **descargar un reporte en Excel**.
* Conocer el **estado de cada estudiante** (Activo, Desertor o Graduado) y su trayectoria semestre a semestre.

---

## 2. INSTALACIÓN Y PUESTA EN MARCHA

### 2.1. En un equipo (Windows)
1. Ejecute el instalador **Setup_UCO_Analytics_3.0.0.exe**. No requiere permisos de administrador.
2. Abra **UCO Analytics** desde el menú Inicio o el escritorio.
3. Se abrirá una ventana de consola y luego el navegador en la dirección `http://127.0.0.1:8000`.
4. **No cierre la ventana de consola** mientras use el sistema. Para salir, ciérrela.
5. La primera vez, la consola muestra la **contraseña temporal del usuario `admin`**. Anótela: no se repite.

### 2.2. En un servidor
El área de sistemas despliega la aplicación con Docker y HTTPS (ver `README.md`). Los usuarios solo necesitan la dirección web (por ejemplo `https://analitica.uco.edu.co`) y pueden ingresar desde computador, tableta o celular.

---

## 3. ACCESO Y USUARIOS

### 3.1. Roles
* **Administrador:** carga y elimina archivos, gestiona usuarios, catálogo de programas y parámetros, consulta la auditoría y todos los indicadores.
* **Consultor:** consulta indicadores, estado por estudiante y descarga reportes. No modifica información.

### 3.2. Primer ingreso y contraseñas
* Todo usuario nuevo recibe una **contraseña temporal** que le entrega el administrador.
* En el primer ingreso el sistema **obliga a definir una contraseña personal**: mínimo 8 caracteres, con letras y números, distinta de la cédula.
* Tras **5 intentos fallidos** el acceso se bloquea temporalmente durante 15 minutos (valores configurables).
* La sesión expira tras 60 minutos (configurable).

### 3.3. Crear usuarios (administrador)
1. Menú **Usuarios** → **＋ Nuevo usuario**.
2. Ingrese la **cédula** (será el usuario), el **nombre completo** y el **rol**.
3. Al guardar, el sistema muestra la **contraseña temporal una sola vez**. Cópiela y entréguela por un canal seguro.

### 3.4. Olvido de contraseña
El administrador usa **Restablecer clave** sobre el usuario. Se genera una nueva contraseña temporal y se cierran las sesiones abiertas de ese usuario.

### 3.5. Cambiar mi contraseña
Menú **Cambiar contraseña** → contraseña actual, nueva y confirmación.

---

## 4. CARGA DE INFORMACIÓN (administrador)

### 4.1. Archivos por periodo
Para cada periodo `AAAA-S` (ej. 2024-1) se cargan tres archivos:
1. **Matriculados**: todos los estudiantes matriculados en el semestre.
2. **Matriculados nuevos**: primíparos del semestre. Sin este archivo no se calcula la cohorte.
3. **Egresados**: graduados con su fecha de grado. Puede cargarse **por semestre** o **por año completo** (no ambos para el mismo año).

### 4.2. Reglas
* Los periodos de **Matriculados** deben ser **consecutivos**. Se puede continuar hacia adelante o agregar historia anterior al primer periodo.
* **Matriculados nuevos** exige que el periodo de matriculados ya esté cargado.
* En egresados, el semestre de cada grado se toma del **mes de la fecha de grado** (enero–junio = semestre 1; julio–diciembre = semestre 2). Si una fecha no corresponde al periodo declarado, la carga se rechaza indicando la fila.
* Si el nombre del archivo indica un periodo distinto al seleccionado, la carga se rechaza para evitar errores. Nombre recomendado: `Matriculados 1-2024.xlsx`, `Matriculados Nuevos 1-2024.xlsx`, `Egresados 1-2024.xlsx` o `Egresados 2024.xlsx`.
* La pantalla **Estado por periodo** muestra qué archivo falta en cada periodo y sugiere la siguiente carga.

### 4.3. Columnas requeridas
* **Matriculados y nuevos:** número de documento y programa (el tipo de documento es opcional).
* **Egresados:** número de identificación, programa y fecha de grado.
* Los nombres de columna pueden variar (por ejemplo "Número", "Número de documento", "Identificación").
* El programa puede venir como código (`IS`) o como nombre (`Ing. De sistemas`).

### 4.4. Programas no reconocidos
Si el archivo trae un programa que no está en el catálogo, el sistema **no carga** hasta que usted indique, para cada uno, si es un **programa nuevo** (con su nivel: pregrado o posgrado) o una forma distinta de escribir un **programa existente**. La decisión se recuerda para próximas cargas.

### 4.5. Corregir una carga
* Para sustituir un archivo, cárguelo de nuevo marcando **Reemplazar el archivo existente**.
* **Eliminar** está disponible en el historial. Un periodo de matriculados intermedio no se puede eliminar (dejaría un hueco); en ese caso use Reemplazar.

---

## 5. CONSULTA DE INDICADORES

### 5.1. Filtros
* **Nivel de formación:** Pregrado (comparable con SPADIES), Posgrado o ambos.
* **Tipo de cálculo:**
  * **Institución (IES):** cambiar de programa dentro de la UCO no es deserción.
  * **Programa:** salir del programa cuenta como deserción del programa.
* **Programas:** todos (por defecto) o una selección.

* **Ventana:** cada indicador muestra los **últimos 10 años** cargados (20 periodos) y como máximo **20 semestres** de trayectoria (S1 a S20). La ventana se indica encima de los indicadores.

### 5.2. Indicadores
| Indicador | Qué mide |
|---|---|
| **TDA** | % de matriculados hace un año que lleva dos periodos sin matrícula y no se graduó. |
| **TAI** | % de matriculados en un periodo que no renueva matrícula en el siguiente. |
| **TDC** | Deserción acumulada de cada cohorte de primíparos, semestre a semestre. |
| **TDPA** | Deserción acumulada promedio de todas las cohortes por semestre. |
| **TGA** | Graduación acumulada de todas las cohortes por semestre. |

Cada indicador muestra su fórmula, una **gráfica** (pase el cursor para ver los valores) y la **tabla** con los conteos. En TDC y TGA puede marcar hasta 8 cohortes para comparar en la gráfica.

### 5.3. Reporte en Excel
El botón **Descargar Excel** genera un libro con la hoja Resumen (conteos por periodo, definiciones y advertencias) y una hoja por indicador con su tabla y gráfica, usando los filtros seleccionados.

### 5.4. Advertencias de datos
Si faltan archivos (por ejemplo egresados de un año), el sistema lo indica sobre los indicadores, porque afecta los resultados.

---

## 6. ESTADO POR ESTUDIANTE
* Resumen de estudiantes **Activos**, **Desertores** y **Graduados** al último periodo cargado, por nivel y programa.
* Listado filtrable y paginado.
* **Consultar trayectoria:** digite el número de documento para ver, periodo a periodo, matrícula, programas, ingreso como primíparo y grados.
* Las consultas individuales quedan registradas en la auditoría (protección de datos personales).

---

## 7. ADMINISTRACIÓN

### 7.1. Catálogo de programas
Permite revisar y corregir el **nivel** (pregrado/posgrado) y el código de cada programa. Cambiar el nivel recalcula de inmediato los indicadores.

### 7.2. Parámetros
Tamaño máximo de archivo, duración de la sesión, longitud mínima de contraseña, intentos de inicio de sesión y tiempo de bloqueo, y nombre institucional para reportes. Las reglas metodológicas de SPADIES no son parametrizables para que las cifras sean comparables con las oficiales.

### 7.3. Auditoría
Registro de inicios de sesión (exitosos y fallidos), creación y edición de usuarios, restablecimiento de claves, cargas y eliminaciones de archivos, cambios de catálogo y parámetros, descargas de reportes y consultas individuales de estudiantes.

---

## 8. PREGUNTAS FRECUENTES

* **¿Por qué mis cifras difieren levemente de SPADIES?** SPADIES depura registros con datos del SNIES. La diferencia media esperada es menor a 1 punto. TDPA y TGA de SPADIES incluyen cohortes desde 1998.
* **¿Por qué la TAI del último periodo aparece vacía?** Requiere el periodo siguiente para saber quién no volvió.
* **¿Por qué los últimos semestres de cada cohorte están vacíos en TDC?** La deserción se confirma con dos periodos sin matrícula.
* **¿Por qué cambió la TDC de una cohorte reciente?** Al cargar periodos nuevos se sabe si un estudiante volvió o se graduó; SPADIES funciona igual.
* **Se rechazó un archivo de egresados por fechas.** Verifique que corresponde al semestre o año seleccionado. Las fechas en texto deben ir como `AAAA-MM-DD` o `DD/MM/AAAA`.
* **No puedo ingresar.** Tras varios intentos fallidos el acceso se bloquea unos minutos. Si olvidó la contraseña, pida al administrador que la restablezca.
