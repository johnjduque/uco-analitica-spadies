# MANUAL DE USUARIO FINAL
## SISTEMA ANALÍTICO DE DESERCIÓN Y PERMANENCIA ESTUDIANTIL (UCO ANALYTICS)
### Universidad Católica de Oriente (UCO) — Metodología SPADIES 3.0 · Versión 3.0

---

## CONTENIDO

1. Introducción
2. Instalación y puesta en marcha (en un equipo, en red local y en línea)
3. Acceso y usuarios
4. Qué hace cada módulo
5. Carga de información
6. Consulta de indicadores: filtros, gráficas e interpretación
7. Estado por estudiante
8. Administración
9. Uso desde el celular
10. Respaldos y actualización
11. Qué hacer cuando se presenta un error
12. Preguntas frecuentes

---

## 1. INTRODUCCIÓN

### 1.1. ¿Qué es UCO Analytics?
UCO Analytics es una aplicación web que calcula los indicadores de deserción y permanencia de la metodología **SPADIES 3.0** a partir de los archivos institucionales de matriculados, matriculados nuevos y egresados. Sus cifras de pregrado coinciden con las publicadas por SPADIES para la UCO con un error medio menor a 1 punto porcentual.

### 1.2. ¿Para qué sirve?
* Consultar los 5 indicadores: **TDA**, **TAI**, **TDC**, **TDPA** y **TGA**.
* Filtrar por **nivel de formación** (pregrado, posgrado o ambos), **tipo de cálculo** (Institución o Programa) y **programas**.
* Ver **gráficas** de cada indicador y **descargar un reporte en Excel**.
* Conocer el **estado de cada estudiante** (Activo, Desertor o Graduado) y su trayectoria semestre a semestre.

### 1.3. Datos personales
Los archivos contienen números de documento de estudiantes (Ley 1581 de 2012). No los comparta por correo ni por mensajería, no los suba a repositorios públicos y entregue usuarios solo a quien los necesite. Cada ingreso, carga, descarga y consulta individual queda registrado en la auditoría.

---

## 2. INSTALACIÓN Y PUESTA EN MARCHA

Hay tres formas de usar el sistema. Elija según cuántas personas lo necesiten:

| Modalidad | Quién la usa | Datos | Requiere |
|---|---|---|---|
| **A. Un solo equipo** | Una persona | Solo en ese equipo | Instalador de Windows |
| **B. Red local** | Varias personas de la misma red | Un equipo "servidor" guarda todo | Instalador + un equipo siempre encendido |
| **C. En línea (servidor)** | Varias personas desde cualquier lugar, incluido el celular | Base de datos central SQL Server | Servidor con Docker y un dominio |

> **Importante:** cada instalación de Windows tiene su **propia base de datos**. Si se instala en dos equipos, **no comparten información**. Para que todos vean lo mismo use la modalidad B o la C.

### 2.1. Modalidad A. En un solo equipo (Windows)
1. Ejecute el instalador **Setup_UCO_Analytics_3.0.0.exe**. No requiere permisos de administrador.
   * Si Windows muestra *"Windows protegió su PC"*, pulse **Más información → Ejecutar de todas formas**. Aparece porque el programa aún no tiene firma digital.
2. Abra **UCO Analytics** desde el menú Inicio o el escritorio.
3. Se abrirá una ventana negra (consola) y luego el navegador en `http://127.0.0.1:8000`. Si el puerto 8000 está ocupado, el sistema usa el siguiente libre y lo indica en la consola.
4. **No cierre la ventana negra** mientras use el sistema. Para salir, ciérrela. Esa ventana **es el servidor**: mientras esté abierta, el sistema funciona aunque cierre el navegador.
5. La primera vez, la consola muestra la **contraseña temporal del usuario `admin`**. Anótela: **no se repite**. Escríbala en el primer campo de la pantalla de cambio de contraseña (ver 3.2).

Los datos quedan en `%LOCALAPPDATA%\UCO_Analytics` (tecla Windows + R, pegue esa ruta y pulse Enter).

**Inicio automático con Windows (opcional).** Durante la instalación aparece la casilla *"Iniciar UCO Analytics automáticamente al iniciar sesión en Windows"*. Si la marca, el servidor se levanta solo cada vez que inicia sesión en el equipo, **minimizado y sin abrir el navegador**; usted solo escribe la dirección (o usa su favorito). Se recomienda en el equipo que atiende a otros usuarios (modalidad B). Para activarlo después de instalar, vuelva a ejecutar el instalador y marque la casilla; para quitarlo, borre el acceso directo **UCO Analytics** de la carpeta de inicio (tecla Windows + R, escriba `shell:startup` y pulse Enter). Si cierra la ventana minimizada, el servidor se apaga.

### 2.2. Modalidad B. Red local (varios usuarios, un equipo servidor)
Úsela si no hay servidor y todos trabajan en la misma red o WiFi de la universidad.

1. Instale el programa **en un solo equipo** que permanezca encendido (el "equipo servidor") y cargue allí la información.
2. En ese equipo cree el archivo `%LOCALAPPDATA%\UCO_Analytics\.env` con este contenido y reinicie la aplicación:
   ```
   APP_HOST=0.0.0.0
   APP_PORT=8000
   ```
3. Permita el puerto en el firewall de Windows (PowerShell **como administrador**):
   ```powershell
   New-NetFirewallRule -DisplayName "UCO Analytics" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private,Domain
   ```
4. Averigüe la IP del equipo servidor: abra PowerShell y escriba `ipconfig`; busque *Dirección IPv4* (por ejemplo `192.168.1.25`). Pida a Sistemas que se la dejen **fija**; si cambia, los demás no podrán entrar.
5. Desde cualquier computador o celular **conectado a la misma red**, abra el navegador en `http://IP-DEL-SERVIDOR:8000` (ej. `http://192.168.1.25:8000`).
6. El administrador crea un usuario por persona (menú **Usuarios**). Nadie más instala nada.

**Limitaciones:** funciona solo si el equipo servidor está encendido y con la ventana negra abierta; la conexión no está cifrada (HTTP), por eso solo debe usarse en una red interna de confianza; no es accesible desde fuera de la universidad.

### 2.3. Modalidad C. En línea (servidor con HTTPS)
Es la modalidad recomendada para uso institucional: todos ven los mismos datos, con conexión cifrada y acceso desde cualquier lugar.

El área de Sistemas despliega la aplicación con Docker (ver `README.md`, sección *Instalación en servidor*). Necesita:
* Un servidor Linux con Docker y Docker Compose.
* Un dominio (por ejemplo `analitica.uco.edu.co`) apuntando al servidor, y los puertos 80 y 443 abiertos.
* Completar el archivo `.env` con el dominio, las contraseñas de la base de datos y la llave de seguridad.

Resultado: los usuarios solo reciben la dirección (`https://analitica.uco.edu.co`), su cédula y una contraseña temporal. No instalan nada y pueden usar computador, tableta o celular. La base de datos es SQL Server y el certificado HTTPS se renueva solo.

---

## 3. ACCESO Y USUARIOS

### 3.1. Roles
* **Administrador:** carga y elimina archivos, gestiona usuarios, catálogo de programas y parámetros, consulta la auditoría y todos los indicadores.
* **Consultor:** consulta indicadores, estado por estudiante y descarga reportes. No modifica información. No ve los módulos de administración.

### 3.2. Primer ingreso y contraseñas
* Todo usuario nuevo recibe una **contraseña temporal** que le entrega el administrador.
* En el primer ingreso el sistema abre la pantalla **"Defina su contraseña"** con tres campos:

  | Campo | Qué escribir |
  |---|---|
  | Contraseña temporal / actual | La **temporal** que le entregaron (no la que desea usar) |
  | Nueva contraseña | La que usará de ahora en adelante |
  | Confirmar nueva contraseña | La misma nueva contraseña |

* La nueva contraseña debe tener **mínimo 8 caracteres, con letras y números**, y no puede ser igual a la cédula ni a la temporal.
* En todos los campos de contraseña hay un **ojo** a la derecha: púlselo para ver lo que escribió y vuelva a pulsarlo para ocultarlo. Es opcional; por defecto la contraseña se muestra oculta. Úselo para verificar que escribió bien la temporal, y procure que nadie más vea la pantalla.
* Tras **5 intentos fallidos** el acceso se bloquea temporalmente durante 15 minutos (valores configurables).
* La sesión expira tras 60 minutos de uso (configurable); basta volver a ingresar.

### 3.3. Crear usuarios (administrador)
1. Menú **Usuarios** → **＋ Nuevo usuario**.
2. Ingrese la **cédula** (será el usuario), el **nombre completo** y el **rol**.
3. Al guardar, el sistema muestra la **contraseña temporal una sola vez**. Cópiela y entréguela por un canal seguro.

### 3.4. Olvido de contraseña
El administrador usa **Restablecer clave** sobre el usuario. Se genera una nueva contraseña temporal y se cierran las sesiones abiertas de ese usuario. Si quien olvidó la clave es el **único administrador**, consulte el apartado 11.3.

### 3.5. Cambiar mi contraseña
Menú **Cambiar contraseña** → contraseña actual, nueva y confirmación.

### 3.6. Cerrar sesión y volver a entrar
Cerrar el navegador o cerrar sesión **no apaga el sistema**. Lo que lo mantiene encendido es la **ventana negra** (modalidad A y B). Según lo que haya cerrado, haga lo siguiente:

| Qué cerró | El sistema sigue encendido | Cómo volver a entrar |
|---|---|---|
| Pestaña o navegador | Sí | Abra el navegador y escriba `http://127.0.0.1:8000` (o la dirección que mostró la ventana negra). Si no pasaron 60 minutos, entra directo; si no, pide usuario y contraseña. Guarde la dirección como favorito. |
| Cerró sesión con **Salir** | Sí | Quedará en la pantalla de inicio de sesión. Si la cerró, abra la dirección de arriba e ingrese con su usuario y contraseña. |
| La ventana negra (o reinició el equipo) | No | Abra **UCO Analytics** desde el menú Inicio o el escritorio. Espere unos segundos a que se abra el navegador e ingrese. Si la dirección no abre, es porque el servidor está apagado. |
| Instaló con **inicio automático** | Sí, al iniciar sesión en Windows | No abra el programa: solo escriba la dirección en el navegador. Si no abre, espere un minuto tras iniciar Windows. |

Notas:
* Los **datos y usuarios no se pierden** al cerrar: quedan guardados en el equipo.
* La contraseña temporal del administrador **solo se muestra la primera vez**; después use la que usted definió.
* No cierre la ventana negra mientras alguien carga un archivo: la carga se interrumpe.
* En red local (modalidad B), los demás usuarios solo pueden entrar mientras el equipo servidor tenga el programa encendido. En línea (modalidad C) basta abrir la dirección web.

---

## 4. QUÉ HACE CADA MÓDULO

El menú lateral (en el celular, el botón ☰) muestra los módulos disponibles según su rol.

| Módulo | Rol | Para qué sirve |
|---|---|---|
| **Indicadores** | Todos | Pantalla principal. Muestra los 5 indicadores con sus gráficas y tablas, y permite descargar el reporte en Excel. |
| **Estado por estudiante** | Todos | Cuenta cuántos estudiantes están Activos, Desertores o Graduados y permite ver la trayectoria de una persona por su documento. |
| **Carga de información** | Administrador | Sube los archivos de matriculados, matriculados nuevos y egresados de cada periodo; muestra qué falta y el historial de cargas. |
| **Catálogo de programas** | Administrador | Lista los programas académicos y su nivel (pregrado/posgrado). Permite corregirlos. |
| **Usuarios** | Administrador | Crea usuarios, cambia roles, restablece contraseñas, desmarca "Usuario activo" para impedir el ingreso y elimina cuentas. |
| **Auditoría** | Administrador | Registro de quién hizo qué y cuándo (ingresos, cargas, descargas, consultas). |
| **Parámetros** | Administrador | Ajustes del sistema: tamaño máximo de archivo, duración de sesión, reglas de contraseña y bloqueo. |
| **Cambiar contraseña** | Todos | Cambia su propia contraseña. |

---

## 5. CARGA DE INFORMACIÓN (administrador)

### 5.1. Qué se sube y en qué orden
Para cada periodo `AAAA-S` (ej. 2024-1) se cargan tres archivos:
1. **Matriculados**: todos los estudiantes matriculados en el semestre.
2. **Matriculados nuevos**: primíparos del semestre. Sin este archivo no se calcula la cohorte.
3. **Egresados**: graduados con su fecha de grado. Puede cargarse **por semestre** o **por año completo** (no ambos para el mismo año).

### 5.2. Paso a paso
1. Menú **Carga de información**.
2. En **Cargar archivo**, elija el **tipo** (Matriculados, Matriculados nuevos o Egresados) y el **periodo**.
3. En el selector de archivo, elija el Excel (`.xlsx`, `.xls`) o CSV desde su computador.
4. Si va a sustituir un archivo ya cargado, marque **Reemplazar el archivo existente de este tipo y periodo**.
5. Pulse el botón verde, que dice por ejemplo **Cargar matriculados 2024-1**, y espere el mensaje de confirmación. Si el archivo trae programas desconocidos, aparece antes una pantalla para resolverlos y se confirma con **Confirmar y cargar** (ver 5.5). La carga procesa el archivo una sola vez; luego los indicadores se calculan en menos de un segundo.
6. Revise **Estado por periodo**: indica qué archivo falta en cada periodo y sugiere la siguiente carga.

**Orden recomendado:** empiece por el periodo más antiguo y avance hacia adelante (2018-1, 2018-2, 2019-1…). En cada periodo cargue primero Matriculados, luego Matriculados nuevos y al final Egresados.

### 5.3. Reglas
* Los periodos de **Matriculados** deben ser **consecutivos**. Se puede continuar hacia adelante o agregar historia anterior al primer periodo.
* **Matriculados nuevos** exige que el periodo de matriculados ya esté cargado.
* En egresados, el semestre de cada grado se toma del **mes de la fecha de grado** (enero–junio = semestre 1; julio–diciembre = semestre 2). Si una fecha no corresponde al periodo declarado, la carga se rechaza indicando la fila.
* Si el nombre del archivo indica un periodo distinto al seleccionado, la carga se rechaza para evitar errores. Nombre recomendado: `Matriculados 1-2024.xlsx`, `Matriculados Nuevos 1-2024.xlsx`, `Egresados 1-2024.xlsx` o `Egresados 2024.xlsx`.

### 5.4. Columnas requeridas
* **Matriculados y nuevos:** número de documento y programa (el tipo de documento es opcional).
* **Egresados:** número de identificación, programa y fecha de grado.
* Los nombres de columna pueden variar (por ejemplo "Número", "Número de documento", "Identificación").
* El programa puede venir como código (`IS`) o como nombre (`Ing. De sistemas`).
* El documento debe ser numérico. Las fechas en texto deben ir como `AAAA-MM-DD` o `DD/MM/AAAA`.

### 5.5. Programas no reconocidos
Si el archivo trae un programa que no está en el catálogo, el sistema **no carga** hasta que usted indique, para cada uno, si es un **programa nuevo** (con su nivel: pregrado o posgrado) o una forma distinta de escribir un **programa existente**. La decisión se recuerda para próximas cargas.

### 5.6. Corregir una carga
* Para sustituir un archivo, cárguelo de nuevo marcando **Reemplazar el archivo existente**.
* **Eliminar** está disponible en el historial. Un periodo de matriculados intermedio no se puede eliminar (dejaría un hueco); en ese caso use Reemplazar.

---

## 6. CONSULTA DE INDICADORES: FILTROS, GRÁFICAS E INTERPRETACIÓN

### 6.1. Filtros
* **Nivel de formación:** Pregrado (comparable con SPADIES), Posgrado o ambos. SPADIES solo publica pregrado, así que posgrado no tiene cifra oficial de referencia.
* **Tipo de cálculo:**
  * **Institución (IES):** cambiar de programa dentro de la UCO **no** es deserción. Responde "¿cuántos estudiantes perdemos como universidad?".
  * **Programa:** salir del programa **sí** cuenta como deserción de ese programa, aunque la persona siga en otro. Responde "¿cuántos estudiantes pierde este programa?". Por eso la cifra por programa suele ser mayor o igual a la de institución.
* **Programas:** todos (por defecto) o una selección. Marque uno o varios y pulse **Aplicar**.
* **Ventana:** cada indicador muestra los **últimos 10 años** cargados (20 periodos) y como máximo **20 semestres** de trayectoria (S1 a S20). La ventana se indica encima de los indicadores.

### 6.2. Los cinco indicadores

| Indicador | Qué mide | Cómo leerlo |
|---|---|---|
| **TDA** — Deserción Anual | De los matriculados hace un año (dos periodos atrás), el % que ya no está y no se graduó. | Una cifra por periodo. Sube o baja en el tiempo. Es el indicador "titular". |
| **TAI** — Ausencia Intersemestral | De los matriculados en un periodo, el % que no renueva matrícula en el siguiente. | Mide cuántos "se van" entre un semestre y otro; algunos regresan después. Es una alerta temprana. |
| **TDC** — Deserción por Cohorte | Para cada grupo de primíparos, el % acumulado que ha desertado semestre a semestre. | Una línea por cohorte; solo sube (acumulado). Permite comparar generaciones. |
| **TDPA** — Deserción Promedio Acumulada | Lo mismo que TDC pero promediando todas las cohortes. | Una sola línea: "en promedio, a S4 ha desertado X %". |
| **TGA** — Graduación Acumulada | % de primíparos que se gradúan hasta cada semestre. | Una línea por cohorte, solo sube. Se compara con la TDC. |

Las fórmulas exactas están en `Documentacion/Formulas_Indicadores_SPADIES.md` y también aparecen en cada pestaña del sistema.

### 6.3. Cómo leer la pantalla
1. **Pestañas** TDA, TAI, TDC, TDPA, TGA: cada una muestra la fórmula, la gráfica y la tabla.
2. **Gráfica:** pase el cursor (o toque en el celular) sobre un punto para ver su valor exacto y el periodo.
3. **Tabla:** muestra los conteos detrás de cada porcentaje (cuántos desertores sobre cuántos matriculados). Úsela para verificar o para citar cifras.
4. **Matrices por cohorte (TDC y TGA):** cada fila es una cohorte y cada columna un semestre de trayectoria (S1…S20). Las celdas tienen **mapa de calor**: cuanto más intenso el color, mayor el valor.
5. **Comparar cohortes:** en TDC y TGA marque en la tabla hasta **8 cohortes** para dibujarlas juntas en la gráfica.
6. **Rango de periodos:** aparece encima de los indicadores; confirme que cubre lo que quiere analizar.

### 6.4. Cómo interpretar los resultados
Los números siguientes son **solo ilustrativos**, no cifras de la UCO.

* **TDA = 9 % en 2023-2** significa: de cada 100 estudiantes matriculados en 2022-2, unos 9 no se matricularon en 2023-1 ni en 2023-2 y no se graduaron.
* **TAI mayor que TDA:** es normal. Parte de las personas ausentes un semestre regresan después, así que la ausencia se convierte en deserción solo si se prolonga.
* **TDC de una cohorte = 30 % en S6:** de cada 100 primíparos de esa cohorte, 30 ya habían abandonado antes del sexto semestre. Una cohorte cuya línea sube más rápido que las demás merece revisión (¿qué cambió en ese ingreso?).
* **TDC ya alto en S1–S2:** indica deserción temprana, típica del primer año.
* **TDPA vs. una cohorte concreta:** si una cohorte está por encima del promedio, perdió más estudiantes que lo habitual.
* **TGA:** compárela con la TDC de la misma cohorte. En semestres avanzados, una TDC alta y una TGA baja indican que casi nadie culmina.
* **Vista Institución vs. Programa:** si un programa tiene mucha más deserción en vista *Programa* que en *Institución*, muchos de sus estudiantes **se cambian a otro programa de la UCO** y no abandonan la universidad.
* **Pregrado vs. posgrado:** solo pregrado se puede contrastar con SPADIES.

### 6.5. Datos vacíos o incompletos (no son errores)
* **TAI del último periodo vacía:** necesita el periodo siguiente para saber quién no volvió.
* **Últimos semestres de cada cohorte vacíos en TDC:** la deserción se confirma con dos periodos sin matrícula.
* **Cifras recientes que cambian al cargar nuevos periodos:** al cargar más información se sabe si un estudiante volvió o se graduó; SPADIES funciona igual.
* **Advertencias de datos:** si falta algún archivo (por ejemplo egresados de un año), el sistema lo muestra encima de los indicadores porque afecta los resultados. Cárguelo antes de sacar conclusiones.

### 6.6. Reporte en Excel
El botón **⬇ Descargar Excel** genera un libro con la hoja **Resumen** (conteos por periodo, definiciones y advertencias) y una hoja por indicador con su tabla y gráfica, usando los **filtros seleccionados**. Cambie los filtros y vuelva a descargar para obtener otro reporte (por ejemplo, uno por programa). Cada descarga queda en la auditoría.

---

## 7. ESTADO POR ESTUDIANTE
* Resumen de estudiantes **Activos**, **Desertores** y **Graduados** al último periodo cargado, por nivel y programa.
  * **Activo:** matriculado en el último periodo o en el anterior.
  * **Desertor:** dos o más periodos consecutivos sin matrícula y sin grado.
  * **Graduado:** obtuvo el título.
* Listado filtrable y paginado.
* **Consultar trayectoria:** digite el número de documento para ver, periodo a periodo, matrícula, programas, ingreso como primíparo y grados.
* Las consultas individuales quedan registradas en la auditoría (protección de datos personales). Consulte solo lo que necesite para su trabajo.

---

## 8. ADMINISTRACIÓN

### 8.1. Catálogo de programas
Permite revisar y corregir el **nivel** (pregrado/posgrado) y el código de cada programa. Cambiar el nivel recalcula de inmediato los indicadores. Revíselo después de cargar un programa nuevo.

### 8.2. Parámetros
Tamaño máximo de archivo, duración de la sesión, longitud mínima de contraseña, intentos de inicio de sesión y tiempo de bloqueo, y nombre institucional para reportes. Las reglas metodológicas de SPADIES no son parametrizables para que las cifras sean comparables con las oficiales.

### 8.3. Auditoría
Registro de inicios de sesión (exitosos y fallidos), creación y edición de usuarios, restablecimiento de claves, cargas y eliminaciones de archivos, cambios de catálogo y parámetros, descargas de reportes y consultas individuales de estudiantes. Úsela para saber quién cargó o descargó información.

---

## 9. USO DESDE EL CELULAR

No hay aplicación que instalar. Abra el navegador del celular (Chrome, Safari, etc.) y escriba la dirección del sistema:
* **En línea:** `https://su-dominio` (desde cualquier red, incluso datos móviles).
* **Red local:** `http://IP-DEL-SERVIDOR:8000`, estando **conectado a la misma WiFi** del equipo servidor.
* **Un solo equipo (modalidad A):** no se puede acceder desde el celular, porque el sistema solo responde en ese equipo.

En pantalla pequeña el menú se abre con el botón **☰** (arriba a la izquierda), los filtros se apilan en una sola columna y las tablas anchas se desplazan de lado. Para ver mejor una gráfica o una matriz por cohorte, gire el celular en horizontal. Puede guardar la dirección como acceso directo en la pantalla de inicio desde el menú del navegador.

---

## 10. RESPALDOS Y ACTUALIZACIÓN

### 10.1. Respaldos
* **Instalación en Windows (modalidades A y B):** cierre la aplicación y copie a una ubicación segura los archivos `datos_uco.db` (y `datos_uco.db-wal` si existe) y `.secret_key` de `%LOCALAPPDATA%\UCO_Analytics`. Contienen datos personales: guárdelos cifrados o en un lugar con acceso restringido. Haga un respaldo después de cada carga importante.
* **Servidor (modalidad C):** Sistemas debe respaldar la base `UCO_Analytics` de SQL Server (o el volumen `mssql_data`) y el archivo `.env`.
* **Restaurar:** con la aplicación cerrada, copie de vuelta los archivos al mismo lugar.

### 10.2. Actualizar a una nueva versión
* **Windows:** ejecute el nuevo instalador sobre el anterior. La base de datos y los usuarios se conservan, y la estructura se actualiza sola al iniciar.
* **Servidor:** Sistemas actualiza el código y ejecuta `docker compose up -d --build`; los datos se conservan en los volúmenes.

---

## 11. QUÉ HACER CUANDO SE PRESENTA UN ERROR

El sistema muestra el motivo en un recuadro rojo. Primero lea el mensaje: casi siempre dice qué corregir.

### 11.1. Errores al ingresar o cambiar la contraseña

| Mensaje | Causa | Qué hacer |
|---|---|---|
| *Cédula o contraseña incorrecta* | Usuario o clave mal escritos. | Revise mayúsculas y que el usuario sea la cédula sin puntos. Si la temporal se copió de la consola, verifique que no tenga espacios al inicio o al final. |
| *Demasiados intentos fallidos. Espere unos minutos…* | Se superaron los intentos permitidos (por defecto 5). | Espere 15 minutos o pida al administrador que restablezca su clave. |
| *La contraseña actual suministrada no es correcta* | En el primer campo no está la clave vigente. | En el primer ingreso, ese campo lleva la **contraseña temporal**, no la nueva. |
| *La contraseña debe tener al menos 8 caracteres* / *debe combinar letras y números* / *no puede ser igual al usuario o cédula* | La nueva clave no cumple la política. | Use 8 o más caracteres con letras y números. |
| *La confirmación no coincide con la nueva contraseña* | Los dos campos nuevos son distintos. | Escriba lo mismo en ambos. |
| *Debe cambiar su contraseña temporal antes de continuar* | Primer ingreso o clave restablecida. | Complete la pantalla "Defina su contraseña". |
| *Usuario inactivo* o no puede ingresar aunque la clave es correcta | El administrador desmarcó "Usuario activo". | Pida al administrador que lo reactive en el módulo **Usuarios**. |
| *Su sesión ha expirado o no es válida* | Pasó el tiempo de sesión o se restableció su clave. | Ingrese de nuevo. |
| *No tiene permisos para realizar esta acción* | Su rol (Consultor) no permite esa opción. | Pida la acción a un administrador. |

### 11.2. Errores al cargar archivos

| Mensaje | Causa | Qué hacer |
|---|---|---|
| *Secuencia cronológica incorrecta* | El periodo no es el siguiente esperado (hay un hueco o falta el periodo previo). | Cargue primero el periodo faltante; revise la sugerencia en **Estado por periodo**. |
| *Este periodo ya fue cargado previamente* | Ya existe ese archivo para ese periodo. | Si es una corrección, marque **Reemplazar el archivo existente**. |
| *El archivo subido no tiene un formato válido* | No es Excel ni CSV, o está dañado. | Guárdelo como `.xlsx` o `.csv` y vuelva a subirlo. |
| *No contiene la columna obligatoria de Documento / Programa / Fecha de Grado* | Falta una columna o su nombre es muy distinto. | Agregue o renombre la columna (ver 5.4). Egresados necesita la fecha de grado. |
| *Existen filas donde el documento no es un número válido* | Hay celdas con letras, vacías o con puntos. | Corrija esas filas (el mensaje indica cuáles) y vuelva a cargar. |
| *El archivo supera el tamaño máximo permitido* | Archivo muy grande. | Divídalo por semestre, o pida al administrador subir el límite en **Parámetros**. |
| *El archivo no contiene registros válidos* | Vacío o con encabezados en una fila inesperada. | Verifique que los datos empiecen en la primera hoja y con encabezados. |
| Rechazo por fechas de grado | Una fecha no corresponde al semestre o año declarado. | Revise las filas indicadas y el periodo elegido. |
| Rechazo por nombre del archivo | El nombre sugiere otro periodo. | Renombre el archivo o seleccione el periodo correcto (ver 5.3). |
| Programas no reconocidos | El archivo trae programas que no están en el catálogo. | Indique en pantalla si son nuevos o equivalentes a uno existente (ver 5.5). |

### 11.3. Errores de consulta y del sistema

| Mensaje o situación | Qué hacer |
|---|---|
| *No hay suficientes datos cargados para calcular…* | Cargue al menos Matriculados y Matriculados nuevos de varios periodos consecutivos. |
| *No se encontraron registros académicos para el documento consultado* | Verifique el número (sin puntos ni espacios) y que ese estudiante esté en los archivos cargados. |
| *Los filtros solicitados no son válidos* | Recargue la página (F5) y vuelva a elegir los filtros. |
| *Ocurrió un error interno en el servidor* | Recargue la página. Si persiste, anote la hora y comuníquese con soporte (el administrador puede ubicar el evento en la auditoría). |
| *No fue posible conectar con la base de datos* | En servidor, avise a Sistemas. En Windows, cierre la aplicación y ábrala de nuevo. |
| La página no abre (modalidad A) | Verifique que la **ventana negra** siga abierta; si la cerró, abra el programa de nuevo (ver 3.6). |
| La página no abre desde otro equipo o celular (modalidad B) | Confirme que el equipo servidor está encendido con la aplicación abierta, que está en la misma red, que la IP no cambió y que el puerto 8000 está permitido en el firewall (ver 2.2). |
| *Windows protegió su PC* al instalar | Pulse **Más información → Ejecutar de todas formas** (ver 2.1). |
| El puerto 8000 está ocupado | El programa elige otro automáticamente; use la dirección que muestre la consola. |
| Se perdió la contraseña del **único administrador** | Se debe reiniciar con una base de datos nueva o pedir soporte técnico; por eso conviene crear un segundo administrador y hacer respaldos. |

Cuando pida ayuda, tenga a mano: **qué estaba haciendo, el texto exacto del mensaje, la hora y el periodo o archivo involucrado**.

---

## 12. PREGUNTAS FRECUENTES

* **¿Por qué mis cifras difieren levemente de SPADIES?** SPADIES depura registros con datos del SNIES. La diferencia media esperada es menor a 1 punto. TDPA y TGA de SPADIES incluyen cohortes desde 1998.
* **¿Por qué la TAI del último periodo aparece vacía?** Requiere el periodo siguiente para saber quién no volvió.
* **¿Por qué los últimos semestres de cada cohorte están vacíos en TDC?** La deserción se confirma con dos periodos sin matrícula.
* **¿Por qué cambió la TDC de una cohorte reciente?** Al cargar periodos nuevos se sabe si un estudiante volvió o se graduó; SPADIES funciona igual.
* **¿Se pueden ver los datos de posgrado?** Sí, con el filtro de nivel. No tienen cifra oficial de SPADIES para comparar.
* **¿Dos computadores con el instalador ven la misma información?** No. Para compartir datos use la red local (2.2) o el servidor en línea (2.3).
* **¿Puedo usar el sistema fuera de la universidad?** Solo en la modalidad en línea (2.3). Las modalidades A y B funcionan únicamente en la red local.
* **¿Se pierde la información al actualizar?** No. La base de datos y los usuarios se conservan.
* **No puedo ingresar.** Tras varios intentos fallidos el acceso se bloquea unos minutos. Si olvidó la contraseña, pida al administrador que la restablezca.
