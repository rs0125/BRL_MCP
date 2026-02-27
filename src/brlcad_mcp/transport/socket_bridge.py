"""TCP socket bridge for sending MGED commands to BRL-CAD's Tcl listener."""

from __future__ import annotations

import logging
import socket

from brlcad_mcp.config import settings

logger = logging.getLogger(__name__)


def send_command(cmd: str) -> str:
    """Send a single MGED command to BRL-CAD via the Tcl socket bridge.

    Opens a short-lived TCP connection, transmits *cmd*, and returns the
    response string from BRL-CAD's listener.

    Raises
    ------
    ConnectionError
        If the Tcl listener is unreachable.
    TimeoutError
        If the listener does not respond within the configured timeout.
    """
    cfg = settings.brlcad
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(cfg.timeout)
            sock.connect((cfg.host, cfg.port))
            sock.sendall(f"{cmd}\n".encode("utf-8"))
            response = sock.recv(cfg.buffer_size).decode("utf-8").strip()
            logger.debug("CMD  → %s", cmd)
            logger.debug("RESP ← %s", response)
            return response
    except socket.timeout as exc:
        raise TimeoutError(
            f"BRL-CAD listener at {cfg.host}:{cfg.port} timed out"
        ) from exc
    except OSError as exc:
        raise ConnectionError(
            f"Could not reach BRL-CAD listener at {cfg.host}:{cfg.port}: {exc}"
        ) from exc
