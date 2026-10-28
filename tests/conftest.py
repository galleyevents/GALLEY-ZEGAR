"""Wspólne przygotowanie testów (jak w GALLEY Presentation Manager).

Testy działają bez monitora (Qt „offscreen” z dwoma wirtualnymi ekranami 1920×1080: LAPTOP główny
+ PROJEKTOR) i na osobnych ustawieniach, więc nie ruszają prawdziwej konfiguracji programu.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_screens = os.path.join(ROOT, ".test_screens.json")
with open(_screens, "w") as f:
    json.dump({"synchronousWindowSystemEvents": False, "windowFrameMargins": False, "screens": [
        {"name": "LAPTOP", "x": 0, "y": 0, "width": 1920, "height": 1080,
         "logicalDpi": 96, "logicalBaseDpi": 96, "dpr": 1},
        {"name": "PROJEKTOR", "x": 1920, "y": 0, "width": 1920, "height": 1080,
         "logicalDpi": 96, "logicalBaseDpi": 96, "dpr": 1}]}, f)
# Qt dzieli ustawienia platformy dwukropkiem - „C:” w ścieżce na Windows ją ucina; bez litery dysku
_screens_qt = os.path.splitdrive(_screens)[1].replace("\\", "/")
os.environ["QT_QPA_PLATFORM"] = f"offscreen:configfile={_screens_qt}"

import galley_zegar.utils as gu                  # noqa: E402
gu.SETTINGS_ORG = "GALLEY-testy"                 # osobne ustawienia na czas testów


def pump(app, seconds):
    """Pozwala programowi „pożyć” przez chwilę (zdarzenia, zegary)."""
    import time
    end = time.time() + seconds
    while time.time() < end:
        app.processEvents()
        time.sleep(0.005)


@pytest.fixture(scope="session")
def app():
    from PySide6.QtWidgets import QApplication
    from galley_zegar.theme import apply_theme
    a = QApplication.instance() or QApplication([])
    a.setQuitOnLastWindowClosed(False)
    a.setStyle("Fusion")
    apply_theme(a, "light")
    return a
