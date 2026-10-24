"""Utilidades compartidas por las pruebas."""

import io

import tests  # noqa: F401  (configura el entorno antes de importar la app)
from fastapi.testclient import TestClient

from app.core import rate_limit
from app.core.database import Base, engine
from app.main import app, initialize_database
from app.services import indicator_service

ADMIN_PWD = "Clave2026Segura"


def reset_database() -> None:
    import app.models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
    initialize_database()
    indicator_service.invalidate_cache()
    rate_limit.clear_all()


def client() -> TestClient:
    return TestClient(app)


def login(c: TestClient, username: str, password: str) -> dict:
    r = c.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


def admin_headers(c: TestClient) -> dict:
    """Inicia sesión con el admin inicial, cambia la clave temporal y retorna cabeceras."""
    try:
        data = login(c, "admin", ADMIN_PWD)
    except AssertionError:
        data = login(c, "admin", "Temporal123")
        r = c.post("/api/auth/change-password", json={"old_password": "Temporal123", "new_password": ADMIN_PWD},
                   headers={"Authorization": f"Bearer {data['token']}"})
        assert r.status_code == 200, r.text
        data = r.json()
    return {"Authorization": f"Bearer {data['token']}"}


def csv_bytes(header, rows) -> bytes:
    out = io.StringIO()
    out.write(";".join(header) + "\n")
    for r in rows:
        out.write(";".join(str(x) for x in r) + "\n")
    return out.getvalue().encode("utf-8")


def upload(c, headers, tipo, periodo, filename, content, reemplazar=False, decisiones=None):
    data = {"tipo": tipo, "periodo": periodo, "reemplazar": str(reemplazar).lower()}
    if decisiones is not None:
        import json
        data["decisiones_programas"] = json.dumps(decisiones)
    return c.post("/api/loads", headers=headers, data=data, files={"file": (filename, content, "text/csv")})
