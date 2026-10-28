"""Dziennik: %LOCALAPPDATA%\\GALLEY Zegar\\zegar.log (do 1 MB, 3 poprzednie)."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

log = logging.getLogger("galley_zegar")
_configured = False


def log_dir():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "GALLEY Zegar")
    base = os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state")
    return os.path.join(base, "galley-zegar")


def setup_logging(level=logging.INFO):
    global _configured
    if _configured:
        return
    _configured = True
    log.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    try:
        os.makedirs(log_dir(), exist_ok=True)
        fh = RotatingFileHandler(os.path.join(log_dir(), "zegar.log"), maxBytes=1_000_000, backupCount=3,
                                 encoding="utf-8")
        fh.setFormatter(fmt)
        log.addHandler(fh)
    except OSError as exc:            # brak prawa zapisu: tylko konsola
        print(f"Nie można utworzyć dziennika: {exc}", file=sys.stderr)

    def excepthook(exc_type, exc, tb):
        log.critical("Nieobsłużony błąd", exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)
    sys.excepthook = excepthook
