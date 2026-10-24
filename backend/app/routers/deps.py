"""Utilidades comunes de los enrutadores."""

from typing import Tuple

from fastapi import Request


def client_info(request: Request) -> Tuple[str, str]:
    """IP del cliente (respeta X-Forwarded-For cuando uvicorn corre con --proxy-headers) y navegador."""
    ip = request.client.host if request.client else "-"
    return ip, request.headers.get("user-agent", "")[:250]
