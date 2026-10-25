"""
PUNTO DE ENTRADA DE ESCRITORIO (ejecutable Windows)

Inicia el servidor local y abre el navegador. Por seguridad escucha solo en
127.0.0.1; para compartir en la red local defina APP_HOST=0.0.0.0 en el .env.
Si el puerto configurado (APP_PORT, por defecto 8000) está ocupado, usa uno libre.
Con el argumento --sin-navegador no abre el navegador (lo usa el inicio automático).
"""

import os
import socket
import sys
import threading
import time
import webbrowser

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import uvicorn  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402


def _free_port(host: str, preferred: int) -> int:
    for port in [preferred] + list(range(preferred + 1, preferred + 50)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host if host != "0.0.0.0" else "", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No se encontró un puerto libre.")


def main():
    host = settings.APP_HOST
    port = _free_port(host, settings.APP_PORT)
    url = f"http://127.0.0.1:{port}"

    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(url)
        except Exception as exc:
            print(f"No se pudo abrir el navegador automáticamente: {exc}")

    # Con --sin-navegador (inicio automático con Windows) solo se levanta el servidor.
    if "--sin-navegador" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()
    print("=" * 70)
    print("   UNIVERSIDAD CATOLICA DE ORIENTE - UCO Analytics")
    print("   Sistema de analitica de desercion y permanencia estudiantil")
    print("=" * 70)
    print(f"   Aplicacion disponible en: {url}")
    print("   Mantenga esta ventana abierta mientras usa el sistema.")
    print("   Para cerrar la aplicacion, cierre esta ventana.")
    print("=" * 70)
    uvicorn.run(app, host=host, port=port, log_level="info", access_log=False)


if __name__ == "__main__":
    main()
