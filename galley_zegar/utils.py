"""Drobiazgi: ustawienia, ikona, ścieżki plików programu (także w .exe)."""

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel

# Testy podmieniają SETTINGS_ORG, żeby nie ruszać prawdziwych ustawień.
SETTINGS_ORG = "GALLEY"
SETTINGS_APP = "Zegar"


def resource_path(name):
    """Plik z głównego folderu programu, np. zegar.ico (działa też w .exe)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, name)


def app_icon():
    path = resource_path("zegar.ico")
    return QIcon(path) if os.path.isfile(path) else QIcon()


def label(text, name=None, wrap=False):
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    w.setWordWrap(wrap)
    return w
