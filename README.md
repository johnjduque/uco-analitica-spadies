# 🎓 UCO Analytics - Sistema de Analítica de Deserción y Permanencia Estudiantil

> **Universidad Católica de Oriente (UCO)**  
> Facultad de Ingeniería • Programa de Ingeniería de Sistemas  
> Implementación del estándar y metodología oficial **SPADIES 3.0** (Ministerio de Educación Nacional de Colombia).

---

## 📌 Descripción General

**UCO Analytics** es una plataforma web integral diseñada para el procesamiento longitudinal de matrículas y graduaciones académicas, permitiendo calcular de forma dinámica los 5 indicadores oficiales de deserción y retención estudiantil estipulados por el Ministerio de Educación Nacional de Colombia bajo el modelo SPADIES:

1. **TDC:** Tasa de Deserción por Cohorte (seguimiento de primíparos $S_1 \dots S_{17}$).
2. **TDPA:** Tasa de Deserción Promedio Acumulada.
3. **TDA:** Tasa de Deserción Anual ($t$ vs. $t - 2$).
4. **TGA:** Tasa de Graduación Acumulada (cruce automático con archivos de egresados).
5. **TAI:** Tasa de Ausencia Intersemestral ($t$ vs. $t - 1$).

Además, incorpora:
* **Seguimiento Individual Longitudinal:** Consulta por número de cédula con línea de tiempo detallada de matrícula y clasificación de estado (*Activo, Desertor, Graduado, Retirado*).
* **Filtro Multiprograma:** Evaluación institucional global o segmentada por cualquiera de los 30 programas académicos oficiales de la UCO.
* **Trazabilidad y Auditoría (Audit Trail):** Registro inmutable en lenguaje ubicuo de todas las operaciones (cargas de archivos, purgas, creación de usuarios y accesos).
* **Seguridad:** Autenticación JWT, contraseñas hasheadas con Bcrypt y control de acceso basado en roles (*Administrador* y *Consultor*).

---

## 🏗️ Arquitectura Técnica

El sistema está construido bajo principios de **Clean Architecture** y separación en capas:

* **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Pandas + OpenPyXL + Bcrypt + PyJWT.
* **Frontend:** React 19 + Vite + Vanilla CSS moderno (Glassmorphism, variables semánticas, responsive design).
* **Base de Datos:** Arquitectura dual transparente:
  * **SQLite:** Por defecto para despliegue local y entornos offline.
  * **Microsoft SQL Server:** Soportado mediante driver ODBC para despliegues institucionales en servidor central.

---

## 🚀 Puesta en Marcha Local

### Prerrequisitos
* Python 3.10+
* Node.js 18+

### 1. Clonar el Repositorio
```bash
git clone https://github.com/johnjduque/uco-analitica-spadies.git
cd uco-analitica-spadies
```

### 2. Configurar y Ejecutar el Backend
```bash
cd backend
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```
*API disponible en:* `http://127.0.0.1:8000`  
*Documentación interactiva Swagger:* `http://127.0.0.1:8000/docs`

### 3. Configurar y Ejecutar el Frontend
```bash
cd ../frontend
npm install
npm run dev
```
*Aplicación web disponible en:* `http://127.0.0.1:5173`

---

## 🐳 Despliegue con Docker

El proyecto cuenta con configuración lista para contenedores Docker:

```bash
docker-compose up --build -d
```

---

## 👥 Credenciales de Acceso por Defecto (Entorno de Pruebas)

| Usuario | Contraseña | Rol | Nombre |
| :--- | :--- | :--- | :--- |
| **admin** | admin123 | Administrador | Administrador Sistema |
| **consultor** | consultor123 | Consultor | Consultor Académico |

---

## 📄 Licencia y Derechos

Desarrollado para la **Universidad Católica de Oriente (UCO)** como proyecto de Analítica Institucional y Gestión de la Permanencia Estudiantil. Todos los derechos reservados.
