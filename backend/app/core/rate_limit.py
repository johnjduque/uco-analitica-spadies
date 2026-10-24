"""
LÍMITE DE INTENTOS DE INICIO DE SESIÓN (protección contra fuerza bruta)

Registro en memoria por (IP, usuario). Suficiente para instalación local y para
un servidor con un solo proceso; en despliegues con varios procesos el límite
aplica por proceso (sigue siendo una barrera efectiva).
"""

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

_lock = threading.Lock()
_failures: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)


def _key(ip: str, username: str) -> Tuple[str, str]:
    return (ip or "-", (username or "").strip().lower())


def seconds_locked(ip: str, username: str, max_attempts: int, window_minutes: int) -> int:
    """Segundos restantes de bloqueo (0 si puede intentar)."""
    now = time.time()
    window = window_minutes * 60
    with _lock:
        q = _failures[_key(ip, username)]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= max_attempts:
            return int(window - (now - q[0])) + 1
    return 0


def register_failure(ip: str, username: str) -> None:
    with _lock:
        _failures[_key(ip, username)].append(time.time())


def reset(ip: str, username: str) -> None:
    with _lock:
        _failures.pop(_key(ip, username), None)


def clear_all() -> None:
    with _lock:
        _failures.clear()
