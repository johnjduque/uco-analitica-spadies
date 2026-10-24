# Guía paso a paso: instalación y uso en Windows

UCO Analytics v3.0 · Probado en Windows 10 (19045) con Python 3.12.4, Node.js 24 e Inno Setup 6.

---

## Parte A. Instalar y usar la aplicación (usuario final)

### A1. Instalar
1. Copie `installer\Output\Setup_UCO_Analytics_3.0.0.exe` al equipo donde se usará (sirve el mismo equipo de desarrollo).
2. Haga doble clic en el instalador.
   - Si Windows muestra **"Windows protegió su PC"** (SmartScreen), haga clic en **Más información → Ejecutar de todas formas**. Aparece porque el instalador no tiene firma digital comercial.
3. Siga el asistente. No pide permisos de administrador: se instala para el usuario actual en `%LOCALAPPDATA%\UCO_Analytics`.
4. Marque **Crear un acceso directo en el escritorio** si lo desea y finalice. Al terminar, la aplicación se abre sola.

### A2. Primer inicio
1. Se abre una **ventana negra (consola)** y, después de unos segundos, el navegador en `http://127.0.0.1:8000`.
2. En la consola aparece un recuadro **ADMINISTRADOR INICIAL CREADO** con:
   - Usuario: `admin`
   - Contraseña temporal: (12 caracteres)
   **Cópiela ahora**: solo se muestra esta vez.
3. En el navegador inicie sesión con `admin` y la contraseña temporal.
4. El sistema pide definir una **contraseña nueva**: mínimo 8 caracteres, con letras y números.
5. **No cierre la consola** mientras use la aplicación. Para salir, cierre la consola.

> Recomendación: cree de inmediato un **segundo administrador** (paso A4). Si el único administrador olvida su contraseña, nadie podrá restablecerla.

### A3. Cargar la información (2018-1 a 2024-2)
Menú **Carga de información**. Por cada periodo, en este orden:

| Paso | Tipo de archivo | Año / Semestre | Archivo de `Datos_UCO` |
|---|---|---|---|
| 1 | Matriculados | 2018 / 1 | `Estudiantes y Egresados\Matriculados 1-2018.xls` |
| 2 | Matriculados nuevos | 2018 / 1 | `EstudiantesNuevos\Matriculados Nuevos 1-2018.xls` |
| 3 | Egresados | 2018 / 1 | `Estudiantes y Egresados\Egresados 1-2018.xls` |
| 4 | Matriculados | 2018 / 2 | `Matriculados 2-2018.xls` |
| … | … | … | … hasta 2024-2 |

- El cuadro **Siguiente carga sugerida** muestra cuál sigue. **Usar sugerencia** llena el tipo y el periodo.
- Para egresados use **o** los archivos semestrales (`Egresados 1-2018`, `Egresados 2-2018`) **o** el anual (`Egresados 2018`, con Semestre = *Año completo*), nunca ambos para el mismo año. Contienen los mismos registros.
- **Programas no reconocidos**: la primera vez aparece una ventana con programas que no están en el catálogo. Con sus archivos aparecen:
  - `EU` (3 registros de egresados): indique a qué programa corresponde, con **Es un programa existente**, o créelo si es nuevo.
  - `Licenciatura en educación básica con énfasis en ciencias naturales y educación ambiental` (1 registro): **Es un programa nuevo**, nivel *Pregrado*.

  La decisión se recuerda para las cargas siguientes.
- La tabla **Estado por periodo** debe quedar sin "Falta" en ninguna columna.
- Si se equivoca de archivo, vuelva a cargarlo marcando **Reemplazar el archivo existente**.

### A4. Crear usuarios
1. Menú **Usuarios → ＋ Nuevo usuario**.
2. Cédula (será el usuario), nombre completo y rol:
   - **Consultor**: ve indicadores, estudiantes y descarga Excel.
   - **Administrador**: además carga datos, gestiona usuarios, programas y parámetros.
3. Copie la **contraseña temporal** que aparece y entréguela al usuario. Al entrar, el usuario debe cambiarla.
4. Si alguien olvida su contraseña: **Restablecer clave** en la fila del usuario.

### A5. Consultar indicadores
Menú **Indicadores**:
1. **Nivel de formación**: *Pregrado* (comparable con SPADIES), *Posgrado* o *Pregrado y posgrado*.
2. **Tipo de cálculo**: *Institución (IES)* o *Programa*.
3. **Programas**: todos, o elija uno o varios y pulse **Aplicar**.
4. Pestañas **TDA, TAI, TDC, TDPA, TGA**: cada una tiene fórmula, gráfica (pase el cursor para ver valores) y tabla. En TDC y TGA marque en la tabla las cohortes que quiere comparar (máximo 8).
5. **Ventana**: se muestran los **últimos 10 años** (20 periodos) y como máximo **20 semestres** de trayectoria. El rango aparece encima de los indicadores.
6. **⬇ Descargar Excel** genera el reporte con los filtros activos: hojas Resumen, TDA, TAI, TDC, TDPA y TGA, con gráficas.

### A6. Estado por estudiante
Menú **Estado por estudiante**: resumen de Activos, Desertores y Graduados; listado filtrable; y **Consultar trayectoria** con el número de documento.

### A7. Dónde quedan los datos y cómo respaldarlos
- Base de datos: `%LOCALAPPDATA%\UCO_Analytics\datos_uco.db`
- Llave de sesiones: `%LOCALAPPDATA%\UCO_Analytics\.secret_key`
- **Respaldo**: cierre la aplicación y copie esos dos archivos (y `datos_uco.db-wal` si existe) a una ubicación segura. Contienen datos personales de estudiantes.
- Para abrir la carpeta: tecla Windows + R → escriba `%LOCALAPPDATA%\UCO_Analytics` → Enter.

### A8. Actualizar a una nueva versión
Ejecute el nuevo instalador sobre la instalación existente. La base de datos y los usuarios se conservan. Al iniciar, la aplicación actualiza la estructura de la base automáticamente.

---

## Parte B. Desarrollo: ejecutar desde el código

### B1. Requisitos (una sola vez)
- **Python 3.12** (python.org, marque *Add python.exe to PATH*).
- **Node.js LTS** (nodejs.org).
- **Git**.
- **Inno Setup 6**: lo instala automáticamente el script del paso C1 (con winget) si falta.

### B2. Limpieza de archivos de la versión anterior (una sola vez)
En el Explorador, clic derecho sobre `scripts\limpiar_archivos_obsoletos.ps1` → **Ejecutar con PowerShell**. Si Windows lo bloquea, abra PowerShell en la carpeta del proyecto y ejecute:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\limpiar_archivos_obsoletos.ps1
```
Elimina 10 módulos viejos que ya no se usan (`app\auth.py`, `app\analytics_engine.py`, etc.), las carpetas `build_temp` y `dist` de la raíz y las cachés `__pycache__`.

### B3. Configuración local (`backend\.env`)
Abra `backend\.env` y deje **vacía** la línea `SECRET_KEY=`. La que tiene es una de las claves publicadas en GitHub; la aplicación la detecta como insegura e igual genera una propia. El resto puede quedar igual (`DB_ENGINE=sqlite`). Si su `.env` no existe, copie `backend\.env.example` como `backend\.env`.

### B4. Ejecutar en modo desarrollo
PowerShell en la carpeta del proyecto:
```powershell
.\.venv\Scripts\Activate.ps1          # activa el entorno virtual (ya creado)
pip install -r backend\requirements-dev.txt
cd backend
python main.py                         # API + aplicación en http://127.0.0.1:8000
```
- La aplicación queda en `http://127.0.0.1:8000`, con la documentación de la API en `/docs`.
- Para editar el frontend con recarga automática, abra otra terminal: `cd frontend`, `npm run dev` y abra `http://127.0.0.1:5173`.
- Después de cambiar el frontend, compílelo con `npm run build` para que lo sirva el backend y lo incluya el instalador.

### B5. Pruebas automáticas
```powershell
cd backend
$env:UCO_DATOS_DIR = "..\Datos_UCO"      # opcional: incluye la validación contra SPADIES
python -m unittest discover -s tests -v
```
Resultado esperado: `Ran 41 tests ... OK`, con la línea *Error medio vs SPADIES: TDA 0.34 pp, TAI 0.42 pp, TDC 0.95 pp*.

---

## Parte C. Generar el instalador

### C1. Un solo paso
Doble clic en **`scripts\generar_instalador.bat`**. El script hace todo en orden y se detiene si algo falla:
1. Verifica Python y Node.js.
2. Instala o actualiza las dependencias en `.venv`.
3. Compila el frontend (`npm ci` y `npm run build`).
4. Ejecuta las 41 pruebas, incluida la validación contra SPADIES si existe `Datos_UCO`.
5. Empaqueta `installer\dist\UcoAnalytics.exe` con PyInstaller.
6. Genera el instalador con Inno Setup (lo instala con winget si falta).

Resultado: **`installer\Output\Setup_UCO_Analytics_3.0.0.exe`** (≈ 47 MB). El registro completo queda en `installer\build_log.txt`. Tarda entre 5 y 10 minutos.

### C2. Cambiar la versión
Antes de generar una versión nueva, cambie `AppVersion` y `OutputBaseFilename` en `installer\setup_installer.iss` (por ejemplo, 3.0.1).

### C3. Probar el ejecutable sin instalar
`installer\dist\UcoAnalytics.exe` funciona como versión portable: crea su base de datos en la misma carpeta. Bórrela después de probar (`datos_uco.db*` y `.secret_key` de `installer\dist`), porque no es la de producción.

---

## Parte D. Antes de subir a GitHub
1. Verifique con `git status` que **no** aparezcan `Datos_UCO`, archivos `.db`, `.env` ni `.secret_key`. El `.gitignore` ya los excluye.
2. `git add -A` · `git commit -m "v3.0: motor SPADIES validado, seguridad, reportes Excel y gráficas"` · `git push`.
3. La contraseña de SQL Server y la clave de firma que estuvieron en el repositorio público ya no deben usarse en ningún servidor.

---

## Problemas frecuentes

| Problema | Solución |
|---|---|
| El navegador no abre | Abra manualmente la dirección que muestra la consola. Si el puerto 8000 está ocupado, la aplicación usa el siguiente libre (8001, 8002…). |
| "Demasiados intentos fallidos" | Espere 15 minutos o pida a otro administrador que restablezca la clave. |
| Antivirus o SmartScreen bloquea el `.exe` | Es habitual con ejecutables empaquetados sin firma. Permita el archivo o pida a sistemas que lo agregue a la lista blanca. |
| Se rechaza un archivo por "nombre del archivo indica otro periodo" | Verifique que el año y el semestre seleccionados coinciden con el nombre del archivo. |
| Se rechazan egresados por fechas | El archivo tiene grados de otro semestre o año. Verifique el periodo elegido. |
| `generar_instalador.bat` falla | Abra `installer\build_log.txt`; la causa aparece en la línea `ERROR:` del final. |
| Quiere usarlo desde otros equipos de la red | La versión de escritorio solo atiende al propio equipo, por seguridad. Para acceso desde cualquier dispositivo use la instalación en servidor con HTTPS (README, sección 3). |
