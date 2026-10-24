# UCO Analytics — Deserción y permanencia estudiantil

> **Universidad Católica de Oriente (UCO)** · Facultad de Ingeniería · Ingeniería de Sistemas
> Implementación de los indicadores de la metodología **SPADIES 3.0** (Ministerio de Educación Nacional).

Aplicación web para calcular, consultar y exportar los indicadores de deserción y permanencia a partir de los
archivos institucionales de matriculados, matriculados nuevos y egresados. Se instala en un equipo (Windows) o en
un servidor (Docker) y se consulta desde cualquier navegador, incluido el celular.

## Qué hace

- **5 indicadores SPADIES**: Deserción Anual (TDA), Ausencia Intersemestral (TAI), Deserción por Cohorte (TDC),
  Deserción Promedio Acumulada (TDPA) y Graduación Acumulada (TGA).
- **Filtros**: nivel de formación (pregrado, posgrado o ambos), tipo de cálculo (Institución o Programa) y
  selección de uno o varios programas.
- **Ventana de análisis**: últimos 10 años (20 periodos) y hasta 20 semestres de trayectoria por indicador.
- **Gráficas interactivas** de cada indicador y matrices por cohorte con mapa de calor.
- **Reporte en Excel** con una hoja por indicador, tablas y gráficas nativas.
- **Estado por estudiante** (Activo, Desertor, Graduado) y trayectoria individual por documento.
- **Carga de archivos** con validaciones: periodos consecutivos, fechas de grado, columnas, documentos,
  programas desconocidos (pregunta antes de cargar) y reemplazo controlado.
- **Seguridad**: roles (administrador y consultor), contraseñas temporales con cambio obligatorio, bloqueo por
  intentos fallidos, sesiones JWT con expiración y auditoría de accesos, cargas, descargas y consultas.

### Exactitud validada

Con los archivos reales 2018-1 a 2024-2, las cifras de pregrado coinciden con las exportaciones oficiales de
SPADIES con un error medio de:

| Indicador | Vista Institución | Vista Programa |
|---|---|---|
| TDA | 0,34 pp | 0,33 pp |
| TAI | 0,42 pp | 0,41 pp |
| TDC | 0,95 pp | 0,89 pp |

Las diferencias residuales se deben a la depuración de registros que hace SPADIES con datos del SNIES.
Las reglas de cálculo están en [`Documentacion/Formulas_Indicadores_SPADIES.md`](Documentacion/Formulas_Indicadores_SPADIES.md).
SPADIES solo publica pregrado: los indicadores de posgrado usan la misma metodología sin referencia oficial.

## Arquitectura

```
backend/            Python 3.11+ · FastAPI · SQLAlchemy 2 · pandas · openpyxl
  app/
    core/           configuración, base de datos, seguridad (JWT, bcrypt, RBAC), migraciones, mensajes
    domain/         reglas puras: periodos y motor de indicadores SPADIES (sin base de datos)
    services/       casos de uso: cargas, indicadores, estudiantes, reportes, usuarios, auditoría
    routers/        API REST /api/* (cada enrutador declara el rol requerido)
    models.py       tablas
  tests/            pruebas automáticas (unidad, API, seguridad, validación contra SPADIES)
frontend/           React 19 + Vite · sin librerías de gráficas (SVG propio)
  src/api/          cliente HTTP con token y manejo de sesión
  src/components/   componentes reutilizables (gráficas, selector de programas, UI)
  src/views/        pantallas
deploy/             proxy HTTPS (Caddy)
installer/          ejecutable (PyInstaller) e instalador de Windows (Inno Setup)
scripts/            compilación de Windows y limpieza
```

Los archivos cargados se procesan una sola vez y se guardan en la base de datos; los indicadores se calculan en
menos de medio segundo y se guardan en caché hasta que cambien los datos.

Bases de datos soportadas: **SQLite** (instalación local, sin configuración) y **Microsoft SQL Server** (servidor).

> 📘 **Paso a paso detallado para Windows** (instalar, cargar datos, usar, generar el instalador y resolver problemas):
> [`Documentacion/Guia_Instalacion_y_Uso_Windows.md`](Documentacion/Guia_Instalacion_y_Uso_Windows.md)

## 1. Ejecución en un equipo (desarrollo)

Requisitos: Python 3.11+ y Node.js 20+.

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/Mac: source .venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env            # opcional: ajuste la configuración
python main.py                    # API en http://127.0.0.1:8000  (documentación en /docs)

# Frontend (otra terminal)
cd frontend
npm ci
npm run dev                       # http://127.0.0.1:5173
```

**Primer ingreso**: si la base está vacía se crea el usuario `admin`. Su contraseña es la definida en
`INITIAL_ADMIN_PASSWORD` del `.env`; si no la define, se genera una temporal que aparece **una sola vez** en la
consola del backend. El sistema obliga a cambiarla en el primer ingreso.

> Si viene de la versión anterior, los usuarios existentes se conservan. Quien todavía tenga la contraseña por
> defecto (`admin123`, `consultor123`) o igual a su cédula deberá cambiarla al ingresar.

## 2. Instalación de escritorio (Windows)

```powershell
.\scripts\build_windows.ps1
```

Genera `installer\Output\Setup_UCO_Analytics_3.0.0.exe`. El instalador no requiere permisos de administrador;
la base de datos queda en `%LOCALAPPDATA%\UCO_Analytics`. Al abrir el programa se inicia el servidor local y el
navegador. Por seguridad solo escucha en el propio equipo (`APP_HOST=127.0.0.1`).

## 3. Instalación en servidor (Docker, con HTTPS)

Requisitos: Docker y Docker Compose en un servidor Linux con los puertos 80 y 443 abiertos.

```bash
cp deploy/env.produccion.example .env     # complete DOMAIN, contraseñas y SECRET_KEY
docker compose up -d --build
docker compose logs app             # contraseña temporal del admin (si no definió INITIAL_ADMIN_PASSWORD)
```

- `proxy` (Caddy) publica la aplicación en `https://DOMAIN` y obtiene el certificado automáticamente.
- `db` (SQL Server) no expone puertos fuera de Docker.
- La aplicación corre como usuario sin privilegios, sin `/docs` y con cabeceras de seguridad.
- Para usar un SQL Server institucional existente, elimine el servicio `db` y configure `SQLSERVER_HOST`,
  `SQLSERVER_USER` y `SQLSERVER_PASSWORD` en `.env` con un usuario dedicado (no `sa`):

```sql
CREATE LOGIN uco_analytics_app WITH PASSWORD = '<contraseña segura>';
CREATE DATABASE UCO_Analytics;
USE UCO_Analytics;
CREATE USER uco_analytics_app FOR LOGIN uco_analytics_app;
ALTER ROLE db_owner ADD MEMBER uco_analytics_app;
```

Copias de seguridad: respalde el volumen `mssql_data` (o la base `UCO_Analytics`) y el archivo `.env`.

## 4. Carga de información

En **Carga de información** (administrador), por cada periodo `AAAA-S`:

1. **Matriculados**: periodos consecutivos, sin saltos.
2. **Matriculados nuevos** (primíparos): definen las cohortes.
3. **Egresados**: por semestre o por año completo. El semestre del grado se toma del mes de la fecha.

Columnas requeridas: número de documento y programa (código o nombre); en egresados, además, fecha de grado. La
pantalla muestra qué falta en cada periodo y sugiere la siguiente carga.

## 5. Pruebas

```bash
cd backend
python -m unittest discover -s tests -v
# Validación contra SPADIES con los archivos reales (opcional):
#   PowerShell:  $env:UCO_DATOS_DIR="..\Datos_UCO"; python -m unittest tests.test_spadies_validation -v
```

## Seguridad y datos personales

Los archivos contienen números de documento de estudiantes (Ley 1581 de 2012). La carpeta `Datos_UCO/`, las bases
`*.db`, los `.env` y la llave `.secret_key` están excluidos del repositorio. No publique el repositorio con datos ni
secretos; si algún secreto estuvo en el historial de Git, cámbielo.

## Licencia

Desarrollado para la Universidad Católica de Oriente. Todos los derechos reservados.
