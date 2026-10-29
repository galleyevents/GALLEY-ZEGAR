"""GALLEY Zegar: sam zegar na pełnym ekranie (zielone tło do kluczowania), sterowanie na pierwszym ekranie."""
import os

import pytest
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage, QPainter

from conftest import ROOT, pump


@pytest.fixture
def zegar(app):
    from galley_zegar import app as z
    z.settings().clear()
    w = z.ClockWindow()
    w.show()
    pump(app, 0.2)
    yield w
    w.close()
    z.settings().clear()
    pump(app, 0.1)


def _render(opt, display, running=False, blink_on=True, size=(960, 540)):
    from galley_zegar.app import paint_clock
    img = QImage(*size, QImage.Format_RGB32)
    p = QPainter(img)
    paint_clock(p, QRectF(0, 0, *size), opt, display, running, blink_on)
    p.end()
    return img


def _colors(img):
    return {img.pixelColor(x, y).name() for x in range(0, img.width(), 4) for y in range(0, img.height(), 4)}


def test_zegar_na_drugim_ekranie_na_zielonym_tle(app, zegar):
    """Sterowanie na ekranie 1 (LAPTOP), zegar sam na ekranie 2 (PROJEKTOR), pełny ekran, zielone tło."""
    from galley_zegar.app import BACKGROUNDS
    assert zegar.cb_screen.currentData() == "PROJEKTOR"
    assert zegar.output.isVisible()
    assert zegar.output.geometry().x() == 1920 and zegar.output.width() == 1920
    img = zegar.output.grab().toImage()
    assert img.pixelColor(5, 5) == QColor(BACKGROUNDS[0][1])          # róg = tło do kluczowania
    assert QColor("#ffffff").name() in _colors(img)                     # białe cyfry
    zegar.toggle_output()
    assert not zegar.output.isVisible() and zegar.btn_output.text() == "Pokaż zegar na ekranie"
    zegar.toggle_output()
    assert zegar.output.isVisible() and zegar.btn_output.text() == "Schowaj zegar"


def test_start_pauza_reset_i_minuty(app, zegar):
    m = zegar.model
    assert m.display() == ("Pozostało", "00:15:00", "normal")          # domyślnie odliczanie 15 min
    zegar.btn_start.click()
    assert m.running and zegar.btn_start.text() == "Pauza"
    m.watch.adjust(60_500)                                              # minęła ponad minuta
    assert m.display()[1] == "00:14:00"
    zegar.btn_start.click()
    assert not m.running and zegar.btn_start.text() == "Start"
    zegar.btn_reset.click()
    assert m.display()[1] == "00:15:00"
    zegar.btn_plus.click()
    assert m.display()[1] == "00:16:00" and zegar.sp_min.value() == 16
    zegar.btn_minus.click()
    zegar.btn_minus.click()
    assert m.display()[1] == "00:14:00"
    zegar.r_up.setChecked(True)                                         # w górę: ±1 min przesuwa zegar
    assert m.display() == ("Czas wystąpienia", "00:00:00", "normal")
    zegar.btn_plus.click()
    assert m.display()[1] == "00:01:00"


def test_kolory_ostrzezen_i_mruganie(app):
    """Ostatnie 2 minuty na żółto, po czasie na czerwono; mruganie bez przezroczystości (kluczowanie)."""
    from galley_zegar.app import DEFAULTS, OVER, WARN, clock_color
    opt = dict(DEFAULTS)
    assert clock_color(opt, "normal", True, True) == QColor(opt["fg"])
    assert clock_color(opt, "warn", True, True) == QColor(WARN)
    assert clock_color(opt, "over", True, True) == QColor(OVER)
    dim = clock_color(opt, "over", True, False)
    assert dim != QColor(OVER) and dim.alpha() == 255
    assert clock_color(opt, "over", False, False) == QColor(OVER)      # w pauzie nie mruga
    opt["warn"] = False
    assert clock_color(opt, "over", True, True) == QColor(opt["fg"])
    img = _render(dict(DEFAULTS), ("Po czasie", "−00:01:20", "over"), running=True)
    assert QColor(OVER).name() in _colors(img)


def test_wyglad_i_ustawienia_zostaja(app, zegar):
    from galley_zegar import app as z
    zegar.cb_bg.setCurrentIndex(1)                                      # niebieski
    zegar._pick_color("bg", zegar.cb_bg)
    zegar.cb_warn.setChecked(False)
    zegar.cb_caption.setChecked(True)
    zegar.sl_size.setValue(50)
    zegar.sp_min.setValue(25)
    opt = z.load_options()
    assert opt["bg"] == z.BACKGROUNDS[1][1] and not opt["warn"] and opt["caption"]
    assert opt["size"] == 50 and opt["limit_min"] == 25
    img = zegar.output.grab().toImage()
    assert img.pixelColor(5, 5) == QColor(z.BACKGROUNDS[1][1])
    # własny kolor (np. z okienka wyboru koloru) pokazany w liście
    zegar.opt["bg"] = "#123456"
    zegar._select_color(zegar.cb_bg, "#123456")
    assert "#123456" in zegar.cb_bg.currentText()


def test_cyfry_mieszcza_sie_na_ekranie(app):
    """Nawet największe cyfry i minus mieszczą się w szerokości ekranu (wąski ekran 4:3)."""
    from galley_zegar.app import DEFAULTS
    opt = dict(DEFAULTS, size=60, fg="#ffffff", bg="#00b140")
    img = _render(opt, ("Po czasie", "−00:59:59", "normal"), size=(800, 600))
    for x in (0, 1, 2, img.width() - 1, img.width() - 2):              # brzegi bez cyfr
        assert all(img.pixelColor(x, y).name() == "#00b140" for y in range(0, img.height(), 3))


def test_instalator_osobny_od_presentera():
    """Osobny program: własny AppId, własny plik .exe i skrót - nic wspólnego z instalatorem Presentera."""
    with open(os.path.join(ROOT, "instalator.iss"), encoding="utf-8-sig") as f:
        iss = f.read()
    assert "5B957D51-F29D-4D53-A123-40DF7B946B0C" not in iss          # AppId Presentera
    assert '#define AppExe "GalleyZegar.exe"' in iss and "--zegar" not in iss
    from galley_zegar import APP_VERSION
    assert f'#define AppVersion "{APP_VERSION}"' in iss


def test_presety_czasu(app, zegar):
    """1.1: gotowe czasy 5 / 10 / 15 / 30 min jednym kliknięciem + własne presety (zapamiętane)."""
    from galley_zegar import app as z
    assert [b.text() for b in zegar.preset_buttons.values()] == ["5 min", "10 min", "15 min", "30 min"]
    assert zegar.preset_buttons[15].isChecked()                         # domyślnie 15 min
    zegar.btn_start.click()
    zegar.model.watch.adjust(90_000)
    zegar.preset_buttons[30].click()                                    # preset: odliczanie, zegar stoi
    assert not zegar.model.running and zegar.model.display()[1] == "00:30:00"
    assert zegar.preset_buttons[30].isChecked() and not zegar.preset_buttons[15].isChecked()
    assert zegar.sp_min.value() == 30 and z.load_options()["limit_min"] == 30
    zegar.btn_plus.click()                                              # 31 min - żaden preset
    assert not any(b.isChecked() for b in zegar.preset_buttons.values())
    # własne presety: dodane, posortowane, zapamiętane, bez powtórek i bez wbudowanych
    assert zegar.add_preset(45) and zegar.add_preset(20) and zegar.add_preset(45) and zegar.add_preset(10)
    assert z.load_custom_presets() == [20, 45]
    assert list(zegar.preset_buttons) == [5, 10, 15, 20, 30, 45]
    zegar.preset_buttons[45].click()
    assert zegar.model.display()[1] == "00:45:00"
    zegar.remove_preset(20)
    assert list(zegar.preset_buttons) == [5, 10, 15, 30, 45] and z.load_custom_presets() == [45]
    assert zegar.btn_add_preset.text() == "+ Własny…"


def test_duze_przyciski_sterowania(app, zegar):
    """1.1: przyciski sterowania czasem duże i czytelne (wysokość i wielkość napisu)."""
    for b in (zegar.btn_start, zegar.btn_reset, zegar.btn_minus, zegar.btn_plus):
        assert b.height() >= 60, b.text()
    assert zegar.btn_start.font().pixelSize() >= 22 or zegar.btn_start.fontInfo().pixelSize() >= 22
    assert all(b.height() >= 48 for b in zegar.preset_buttons.values())


def test_przebudowa_presetow_nie_zostawia_przyciskow(app, zegar):
    """Po dodaniu / usunięciu presetu w oknie są tylko aktualne przyciski (stare nie leżą na podglądzie)."""
    from PySide6.QtWidgets import QPushButton
    zegar.add_preset(20)
    zegar.remove_preset(20)
    pump(app, 0.1)
    shown = [b.text() for b in zegar.findChildren(QPushButton) if b.isVisibleTo(zegar) and b.objectName() == "Preset"]
    assert sorted(shown) == sorted(["5 min", "10 min", "15 min", "30 min"])
