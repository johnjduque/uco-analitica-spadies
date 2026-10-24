"""Pruebas de seguridad de la API: autenticación, roles, contraseñas y cabeceras."""

import unittest

from tests.helpers import ADMIN_PWD, admin_headers, client, login, reset_database

ADMIN_ROUTES = [
    ("get", "/api/users"), ("post", "/api/users"), ("put", "/api/users/1"), ("delete", "/api/users/1"),
    ("post", "/api/users/1/reset-password"), ("get", "/api/loads"), ("get", "/api/loads/status"),
    ("post", "/api/loads"), ("delete", "/api/loads/1"), ("get", "/api/audit-logs"), ("get", "/api/parameters"),
    ("put", "/api/parameters/X"), ("post", "/api/programs"), ("put", "/api/programs/1"),
]
USER_ROUTES = [
    ("get", "/api/indicators"), ("get", "/api/indicators/export"), ("get", "/api/indicators/programs"),
    ("get", "/api/students/summary"), ("get", "/api/students/123"), ("get", "/api/programs"),
]


class SecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reset_database()
        cls.c = client()
        cls.admin = admin_headers(cls.c)
        r = cls.c.post("/api/users", headers=cls.admin, json={"username": "1036000111", "nombre": "Consultor Prueba", "role": "consultor"})
        assert r.status_code == 200, r.text
        cls.consultor_tmp = r.json()["temporary_password"]
        cls.consultor_id = r.json()["user"]["id"]

    def _consultor_headers(self):
        try:
            data = login(self.c, "1036000111", "Consultor2026x")
        except AssertionError:
            data = login(self.c, "1036000111", self.consultor_tmp)
            r = self.c.post("/api/auth/change-password", json={"old_password": self.consultor_tmp, "new_password": "Consultor2026x"},
                            headers={"Authorization": f"Bearer {data['token']}"})
            self.assertEqual(r.status_code, 200, r.text)
            data = r.json()
        return {"Authorization": f"Bearer {data['token']}"}

    def test_all_protected_routes_reject_anonymous(self):
        for method, url in ADMIN_ROUTES + USER_ROUTES:
            r = getattr(self.c, method)(url)
            self.assertEqual(r.status_code, 401, f"{method.upper()} {url} -> {r.status_code}")

    def test_admin_routes_forbidden_for_consultor(self):
        h = self._consultor_headers()
        for method, url in ADMIN_ROUTES:
            kwargs = {"headers": h}
            if method in ("post", "put") and "loads" not in url and "reset" not in url:
                kwargs["json"] = {"username": "x1234", "nombre": "abc", "role": "consultor", "value": "1", "nombre_": "x"}
            r = getattr(self.c, method)(url, **kwargs)
            self.assertEqual(r.status_code, 403, f"{method.upper()} {url} -> {r.status_code}")
        for method, url in USER_ROUTES:
            r = getattr(self.c, method)(url, headers=h)
            self.assertNotIn(r.status_code, (401, 403), f"{url} -> {r.status_code}")

    def test_bootstrap_endpoint_removed(self):
        r = self.c.post("/api/crear-usuario", json={"username": "hacker", "password": "x"})
        self.assertIn(r.status_code, (404, 405))

    def test_temporary_password_must_be_changed(self):
        r = self.c.post("/api/users", headers=self.admin, json={"username": "1036000222", "nombre": "Nuevo Usuario", "role": "consultor"})
        tmp = r.json()["temporary_password"]
        data = login(self.c, "1036000222", tmp)
        self.assertTrue(data["user"]["must_change_password"])
        h = {"Authorization": f"Bearer {data['token']}"}
        self.assertEqual(self.c.get("/api/indicators", headers=h).json()["error"]["code"], "AUTH_006")
        self.assertEqual(self.c.get("/api/auth/me", headers=h).status_code, 200)

    def test_password_policy(self):
        data = login(self.c, "admin", ADMIN_PWD)
        h = {"Authorization": f"Bearer {data['token']}"}
        for bad in ("corta1", "solamenteletras", "12345678901"):
            r = self.c.post("/api/auth/change-password", json={"old_password": ADMIN_PWD, "new_password": bad}, headers=h)
            self.assertEqual(r.status_code, 400, bad)

    def test_token_invalid_after_password_reset(self):
        h = self._consultor_headers()
        self.assertEqual(self.c.get("/api/indicators", headers=h).status_code, 200)
        import time; time.sleep(1.1)
        r = self.c.post(f"/api/users/{self.consultor_id}/reset-password", headers=self.admin)
        self.assertEqual(r.status_code, 200)
        type(self).consultor_tmp = r.json()["temporary_password"]
        self.assertEqual(self.c.get("/api/indicators", headers=h).status_code, 401)

    def test_tampered_token_rejected(self):
        token = self.admin["Authorization"].split()[1]
        bad = token[:-2] + ("AA" if token[-2:] != "AA" else "BB")
        self.assertEqual(self.c.get("/api/users", headers={"Authorization": f"Bearer {bad}"}).status_code, 401)

    def test_cannot_delete_self_or_last_admin(self):
        me = self.c.get("/api/auth/me", headers=self.admin).json()
        r = self.c.delete(f"/api/users/{me['id']}", headers=self.admin)
        self.assertEqual(r.json()["error"]["code"], "USER_005")
        r = self.c.put(f"/api/users/{me['id']}", headers=self.admin,
                       json={"username": "admin", "nombre": "Administrador", "role": "consultor"})
        self.assertEqual(r.json()["error"]["code"], "USER_005")

    def test_invalid_role_rejected(self):
        r = self.c.post("/api/users", headers=self.admin, json={"username": "1036000333", "nombre": "Rol Malo", "role": "superadmin"})
        self.assertEqual(r.json()["error"]["code"], "USER_004")

    def test_login_lockout(self):
        for _ in range(5):
            self.c.post("/api/auth/login", json={"username": "victima", "password": "malo"})
        r = self.c.post("/api/auth/login", json={"username": "victima", "password": "malo"})
        self.assertEqual(r.status_code, 429)

    def test_security_headers(self):
        r = self.c.get("/api/health")
        for h in ("X-Content-Type-Options", "X-Frame-Options", "Content-Security-Policy", "Referrer-Policy"):
            self.assertIn(h, r.headers)
        self.assertEqual(r.headers["Cache-Control"], "no-store")

    def test_errors_do_not_leak_internals(self):
        r = self.c.get("/api/indicators?nivel=xx", headers=self.admin)
        body = r.text.lower()
        self.assertNotIn("traceback", body)
        self.assertNotIn("sqlalchemy", body)

    def test_path_traversal_static(self):
        r = self.c.get("/../backend/.secret_key")
        self.assertNotIn("secret", r.text.lower()[:200] if r.headers.get("content-type", "").startswith("text/plain") else "")
        r = self.c.get("/%2e%2e/%2e%2e/etc/passwd")
        self.assertNotIn("root:", r.text)


if __name__ == "__main__":
    unittest.main()
