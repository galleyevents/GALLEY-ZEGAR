"""GALLEY Zegar (prośba właściciela, 10.2026): sam zegar „Czas wystąpienia”, bez slajdów.

Ekran 1: okno sterowania (podgląd, Start / Pauza / Resetuj zegar, ±1 min, tryb, wygląd, wybór ekranu).
Ekran 2: zegar na pełnym ekranie na jednolitym tle - domyślnie zielonym, do kluczowania w vMixie.

Liczy dokładnie tak jak zegar w widoku prelegenta GALLEY Presentation Manager (`timer.py`):
w górę albo odliczanie, ostatnie 2 minuty na żółto, po czasie na minusie na czerwono i mruga.
Osobny program: własne ustawienia, dziennik (`zegar.log`) i instalator - nie miesza się z Presenterem.
Start: `python zegar.py` ze źródeł, po instalacji `GalleyZegar.exe` (skrót „GALLEY Zegar”).
"""

import sys

from PySide6.QtCore import QElapsedTimer, QRectF, QSettings, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QGuiApplication, QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QColorDialog, QComboBox, QGridLayout,
                               QHBoxLayout, QMainWindow, QPushButton, QRadioButton, QSlider, QSpinBox,
                               QVBoxLayout, QWidget)

from . import APP_NAME, APP_VERSION, utils
from .log import log
from .screens import place_fullscreen, screen_label, sorted_screens
from .timer import Stopwatch, timer_display
from .utils import label

APP_TITLE = APP_NAME

# Tła do kluczowania: zielony i niebieski „telewizyjny” (vMix: Chroma Key -> kolor tła), czarny do Luma Key.
BACKGROUNDS = (("Zielony – do kluczowania", "#00B140"), ("Niebieski – do kluczowania", "#0047BB"),
               ("Czarny", "#000000"))
DIGITS = (("Białe", "#FFFFFF"), ("Czarne", "#000000"), ("Złote", "#D9A441"))
WARN, OVER = "#F5C451", "#E5484D"    # jak na stronie zegara w sieci (3.13) - bez zielonego (kluczowanie)
BLINK_MS = 800                       # po czasie: jasne / przygaszone co tyle
TICK_MS = 100                        # odświeżanie (sekundy zmieniają się równo)

DEFAULTS = {"mode": "down", "limit_min": 15, "overtime": True, "bg": BACKGROUNDS[0][1],
            "fg": DIGITS[0][1], "size": 34, "warn": True, "caption": False, "screen": ""}


def settings():
    return QSettings(utils.SETTINGS_ORG, utils.SETTINGS_APP)


def load_options():
    s = settings()
    o = dict(DEFAULTS)
    for k, v in DEFAULTS.items():
        o[k] = s.value(k, v, type=type(v))
    o["mode"] = o["mode"] if o["mode"] in ("up", "down") else "down"
    o["limit_min"] = max(1, min(600, o["limit_min"]))
    o["size"] = max(10, min(60, o["size"]))
    for key in ("bg", "fg"):
        if not QColor(o[key]).isValid():
            o[key] = DEFAULTS[key]
    return o


def clock_color(opt, state, running, blink_on):
    """Kolor cyfr: zwykły, żółty (ostatnie 2 min), czerwony (po czasie - przygaszony co drugi takt)."""
    if not opt["warn"] or state == "normal":
        return QColor(opt["fg"])
    if state == "warn":
        return QColor(WARN)
    color = QColor(OVER)
    if state == "over" and running and not blink_on:
        # mruganie BEZ przezroczystości: półprzezroczyste cyfry mieszałyby się z tłem do kluczowania
        color = color.darker(170)
    return color


def paint_clock(p, rect, opt, display, running, blink_on):
    """Rysuje zegar: tło, cyfry wyśrodkowane, (opcjonalnie) podpis nad nimi. Wspólne dla ekranu zegara
    i podglądu w oknie sterowania - podgląd wygląda dokładnie jak wyjście, tylko mniejszy."""
    caption, text, state = display
    p.fillRect(rect, QColor(opt["bg"]))
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    f = QFont("Segoe UI")
    f.setBold(True)
    f.setPixelSize(max(6, int(rect.height() * opt["size"] / 100)))
    width = QFontMetricsF(f).horizontalAdvance("−00:00:00")        # stała szerokość - cyfry nie skaczą
    if width > rect.width() * 0.94:
        f.setPixelSize(max(6, int(f.pixelSize() * rect.width() * 0.94 / width)))
    color = clock_color(opt, state, running, blink_on)
    fm = QFontMetricsF(f)
    h = fm.height()
    cap_h = 0.0
    cf = QFont(f)
    if opt["caption"] and caption:
        cf.setPixelSize(max(6, int(f.pixelSize() * 0.3)))
        cap_h = QFontMetricsF(cf).height() * 1.1
    top = rect.y() + (rect.height() - h - cap_h) / 2
    p.setPen(color)
    if cap_h:
        p.setFont(cf)
        p.drawText(QRectF(rect.x(), top, rect.width(), cap_h), Qt.AlignHCenter | Qt.AlignBottom, caption)
    p.setFont(f)
    p.drawText(QRectF(rect.x(), top + cap_h, rect.width(), h), Qt.AlignCenter, text)


class ClockModel:
    """Stan zegara: stoper z pauzą + tryb (w górę / odliczanie), czas wystąpienia, minus po czasie."""

    def __init__(self, opt):
        self.opt = opt
        self.watch = Stopwatch()

    @property
    def running(self):
        return self.watch.running

    def display(self):
        return timer_display(self.watch.elapsed_ms(), self.opt["mode"], self.opt["limit_min"] * 60000,
                             self.opt["overtime"])

    def toggle(self):
        (self.watch.pause if self.watch.running else self.watch.start)()

    def reset(self):
        """Od początku; zegar, który chodził, chodzi dalej (jak T w widoku prelegenta)."""
        self.watch.reset()

    def adjust(self, minutes):
        """Odliczanie: czas wystąpienia ± minuty (1-600). W górę: zegar przesunięty o ± minuty."""
        if self.opt["mode"] == "down":
            self.opt["limit_min"] = max(1, min(600, self.opt["limit_min"] + minutes))
        else:
            self.watch.adjust(minutes * 60000)


class ClockView(QWidget):
    """Sam zegar: okno na pełnym ekranie (wyjście) albo podgląd w oknie sterowania."""

    def __init__(self, owner, output=False, parent=None):
        flags = (Qt.Window | Qt.FramelessWindowHint) if output else Qt.Widget
        super().__init__(parent, flags)
        self.owner = owner
        self.output = output
        if output:
            self.setWindowTitle(f"{APP_TITLE} – ekran zegara")
            self.setCursor(Qt.BlankCursor)
            self.setAttribute(Qt.WA_OpaquePaintEvent)
        else:
            self.setMinimumSize(320, 180)
            sp = self.sizePolicy()
            sp.setHeightForWidth(True)          # podgląd w proporcjach ekranu, przyciski tuż pod nim
            self.setSizePolicy(sp)

    def _aspect(self):
        t = self.owner._target() if hasattr(self.owner, "cb_screen") else None
        g = t.geometry() if t is not None else None
        return g.width() / g.height() if g is not None and g.height() else 16 / 9

    def hasHeightForWidth(self):
        return not self.output

    def heightForWidth(self, w):
        return int(w / self._aspect())

    def paintEvent(self, _):
        p = QPainter(self)
        o = self.owner
        rect = QRectF(self.rect())
        if not self.output:
            # podgląd w proporcjach ekranu zegara (wielkość cyfr liczona od wysokości ekranu)
            from .theme import T
            p.fillRect(rect, QColor(T["canvas"]))
            aspect = self._aspect()
            w = min(rect.width(), rect.height() * aspect)
            h = w / aspect
            rect = QRectF(rect.x() + (rect.width() - w) / 2, rect.y(), w, h)
        paint_clock(p, rect, o.opt, o.model.display(), o.model.running, o.blink_on())
        p.end()

    def keyPressEvent(self, e):
        # ekran zegara na tym samym monitorze co sterowanie: Esc chowa zegar, reszta jak w oknie sterowania
        if self.output and e.key() == Qt.Key_Escape:
            self.owner.hide_output()
            return
        self.owner.handle_key(e)


class ClockWindow(QMainWindow):
    """Okno sterowania (ekran 1)."""

    def __init__(self, auto_show=True):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} {APP_VERSION}")
        self.opt = load_options()
        self.model = ClockModel(self.opt)
        self._blink = QElapsedTimer()
        self._blink.start()
        self.output = ClockView(self, output=True)
        self._build()
        self.refresh_screens()
        self._sync_controls()
        self._tick = QTimer(self)
        self._tick.setInterval(TICK_MS)
        self._tick.timeout.connect(self._update_views)
        self._tick.start()
        app = QGuiApplication.instance()
        app.screenAdded.connect(lambda *_: QTimer.singleShot(700, self.refresh_screens))
        app.screenRemoved.connect(lambda *_: QTimer.singleShot(700, self.refresh_screens))
        for keys, slot in (("Space", self.toggle), ("T", self.reset), ("+", lambda: self.adjust(+1)),
                           ("=", lambda: self.adjust(+1)), ("-", lambda: self.adjust(-1)),
                           ("F11", self.toggle_output)):
            QShortcut(QKeySequence(keys), self, activated=slot)
        if auto_show:
            QTimer.singleShot(0, self._auto_show)
        log.info("Start %s %s", APP_TITLE, APP_VERSION)

    # ---- budowa okna -----------------------------------------------------------
    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        lay = QHBoxLayout(root)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(18)

        left = QVBoxLayout()
        left.setSpacing(10)
        left.addWidget(label("Podgląd ekranu zegara", "Section"))
        self.preview = ClockView(self)
        left.addWidget(self.preview)
        row = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.setObjectName("Primary")
        self.btn_start.setToolTip("Start / pauza (spacja)")
        self.btn_start.clicked.connect(self.toggle)
        self.btn_reset = QPushButton("Resetuj zegar")
        self.btn_reset.setToolTip("Od początku (T); chodzący zegar liczy dalej od nowa")
        self.btn_reset.clicked.connect(self.reset)
        self.btn_minus = QPushButton("−1 min")
        self.btn_minus.setToolTip("Odliczanie: krótszy czas wystąpienia; w górę: zegar cofnięty (−)")
        self.btn_minus.clicked.connect(lambda: self.adjust(-1))
        self.btn_plus = QPushButton("+1 min")
        self.btn_plus.setToolTip("Odliczanie: dłuższy czas wystąpienia; w górę: zegar do przodu (+)")
        self.btn_plus.clicked.connect(lambda: self.adjust(+1))
        for b in (self.btn_start, self.btn_reset, self.btn_minus, self.btn_plus):
            b.setMinimumHeight(44)
            row.addWidget(b, 2 if b is self.btn_start else 1)
        left.addLayout(row)
        left.addStretch(1)
        lay.addLayout(left, 3)

        right = QVBoxLayout()
        right.setSpacing(8)
        right.addWidget(label("Czas", "Section"))
        self.r_up = QRadioButton("Liczy w górę od zera")
        self.r_down = QRadioButton("Odlicza czas wystąpienia:")
        group = QButtonGroup(self)
        group.addButton(self.r_up)
        group.addButton(self.r_down)
        right.addWidget(self.r_up)
        drow = QHBoxLayout()
        drow.addWidget(self.r_down)
        self.sp_min = QSpinBox()
        self.sp_min.setRange(1, 600)
        self.sp_min.setSuffix(" min")
        self.sp_min.setFixedWidth(100)
        drow.addWidget(self.sp_min)
        drow.addStretch(1)
        right.addLayout(drow)
        self.cb_over = QCheckBox("Po czasie liczy dalej na minusie")
        right.addWidget(self.cb_over)
        self.r_up.toggled.connect(self._options_changed)
        self.sp_min.valueChanged.connect(self._options_changed)
        self.cb_over.toggled.connect(self._options_changed)

        right.addSpacing(10)
        right.addWidget(label("Wygląd", "Section"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.addWidget(label("Tło:"), 0, 0)
        self.cb_bg = QComboBox()
        for name, value in BACKGROUNDS:
            self.cb_bg.addItem(name, value)
        self.cb_bg.addItem("Inny kolor…", "")
        self.cb_bg.activated.connect(lambda _i: self._pick_color("bg", self.cb_bg))
        grid.addWidget(self.cb_bg, 0, 1)
        grid.addWidget(label("Cyfry:"), 1, 0)
        self.cb_fg = QComboBox()
        for name, value in DIGITS:
            self.cb_fg.addItem(name, value)
        self.cb_fg.addItem("Inny kolor…", "")
        self.cb_fg.activated.connect(lambda _i: self._pick_color("fg", self.cb_fg))
        grid.addWidget(self.cb_fg, 1, 1)
        grid.addWidget(label("Wielkość:"), 2, 0)
        self.sl_size = QSlider(Qt.Horizontal)
        self.sl_size.setRange(10, 60)
        self.sl_size.valueChanged.connect(self._options_changed)
        grid.addWidget(self.sl_size, 2, 1)
        right.addLayout(grid)
        self.cb_warn = QCheckBox("Ostrzeżenia: ostatnie 2 minuty na żółto, po czasie na czerwono")
        self.cb_caption = QCheckBox("Podpis nad zegarem („Pozostało”, „Po czasie”)")
        for c in (self.cb_warn, self.cb_caption):
            c.toggled.connect(self._options_changed)
            right.addWidget(c)

        right.addSpacing(10)
        right.addWidget(label("Ekran zegara", "Section"))
        self.cb_screen = QComboBox()
        self.cb_screen.activated.connect(self._screen_chosen)
        right.addWidget(self.cb_screen)
        self.btn_output = QPushButton("Pokaż zegar na ekranie")
        self.btn_output.setToolTip("Zegar na pełnym ekranie na wybranym monitorze (F11)")
        self.btn_output.clicked.connect(self.toggle_output)
        right.addWidget(self.btn_output)
        self.lb_screen = label("", "Muted", wrap=True)
        right.addWidget(self.lb_screen)
        right.addStretch(1)
        right.addWidget(label("Spacja: start / pauza · T: resetuj zegar · + / −: minuta · F11: ekran zegara",
                              "Muted", wrap=True))
        lay.addLayout(right, 2)
        self.resize(1100, 560)

    def _sync_controls(self):
        o = self.opt
        for w in (self.r_up, self.sp_min, self.cb_over, self.sl_size, self.cb_warn, self.cb_caption):
            w.blockSignals(True)
        (self.r_down if o["mode"] == "down" else self.r_up).setChecked(True)
        self.sp_min.setValue(o["limit_min"])
        self.cb_over.setChecked(o["overtime"])
        self.sl_size.setValue(o["size"])
        self.cb_warn.setChecked(o["warn"])
        self.cb_caption.setChecked(o["caption"])
        for w in (self.r_up, self.sp_min, self.cb_over, self.sl_size, self.cb_warn, self.cb_caption):
            w.blockSignals(False)
        self._select_color(self.cb_bg, o["bg"])
        self._select_color(self.cb_fg, o["fg"])
        down = o["mode"] == "down"
        self.sp_min.setEnabled(down)
        self.cb_over.setEnabled(down)
        self._update_views()

    @staticmethod
    def _select_color(combo, value):
        """Kolor z listy albo własny („Inny kolor…” z próbką koloru w nazwie)."""
        i = next((k for k in range(combo.count()) if (combo.itemData(k) or "").lower() == value.lower()), -1)
        if i < 0:
            i = combo.count() - 1
            combo.setItemText(i, f"Inny kolor… ({value.upper()})")
        else:
            combo.setItemText(combo.count() - 1, "Inny kolor…")
        combo.setCurrentIndex(i)

    def _pick_color(self, key, combo):
        value = combo.currentData()
        if not value:                         # „Inny kolor…”
            color = QColorDialog.getColor(QColor(self.opt[key]), self, "Wybierz kolor")
            if not color.isValid():
                self._select_color(combo, self.opt[key])
                return
            value = color.name()
        self.opt[key] = value
        self._select_color(combo, value)
        self._save()

    def _options_changed(self, *_):
        o = self.opt
        o["mode"] = "up" if self.r_up.isChecked() else "down"
        o["limit_min"] = self.sp_min.value()
        o["overtime"] = self.cb_over.isChecked()
        o["size"] = self.sl_size.value()
        o["warn"] = self.cb_warn.isChecked()
        o["caption"] = self.cb_caption.isChecked()
        self.sp_min.setEnabled(o["mode"] == "down")
        self.cb_over.setEnabled(o["mode"] == "down")
        self._save()

    def _save(self):
        s = settings()
        for k, v in self.opt.items():
            s.setValue(k, v)
        self._update_views()

    # ---- zegar -------------------------------------------------------------------
    def blink_on(self):
        return (self._blink.elapsed() // BLINK_MS) % 2 == 0

    def _update_views(self):
        self.btn_start.setText("Pauza" if self.model.running else "Start")
        self.preview.update()
        if self.output.isVisible():
            self.output.update()

    def toggle(self):
        self.model.toggle()
        log.info("Zegar: %s (%s)", "start" if self.model.running else "pauza", self.model.display()[1])
        self._update_views()

    def reset(self):
        self.model.reset()
        log.info("Zegar: reset")
        self._update_views()

    def adjust(self, minutes):
        self.model.adjust(minutes)
        if self.opt["mode"] == "down":
            self.sp_min.blockSignals(True)
            self.sp_min.setValue(self.opt["limit_min"])
            self.sp_min.blockSignals(False)
            self._save()
        self._update_views()

    def handle_key(self, e):
        k = e.key()
        if k == Qt.Key_Space:
            self.toggle()
        elif k == Qt.Key_T:
            self.reset()
        elif k in (Qt.Key_Plus, Qt.Key_Equal):
            self.adjust(+1)
        elif k == Qt.Key_Minus:
            self.adjust(-1)
        elif k == Qt.Key_F11:
            self.toggle_output()

    # ---- ekran zegara --------------------------------------------------------------
    def refresh_screens(self):
        screens = sorted_screens()
        current = self.cb_screen.currentData() or self.opt["screen"]
        self.cb_screen.blockSignals(True)
        self.cb_screen.clear()
        for n, s in enumerate(screens, 1):
            self.cb_screen.addItem(screen_label(n, s), s.name())
        names = [s.name() for s in screens]
        if current not in names:
            primary = QGuiApplication.primaryScreen().name()
            current = next((n for n in names if n != primary), names[0] if names else "")
        if names:
            self.cb_screen.setCurrentIndex(names.index(current))
        self.cb_screen.blockSignals(False)
        if self.output.isVisible() and self._target() is None:
            self.hide_output()                # monitor z zegarem odłączony
        elif self.output.isVisible():
            place_fullscreen(self.output, self._target())
        self._update_screen_info()

    def _target(self):
        name = self.cb_screen.currentData()
        return next((s for s in QGuiApplication.screens() if s.name() == name), None)

    def _screen_chosen(self, _i):
        self.opt["screen"] = self.cb_screen.currentData() or ""
        self._save()
        if self.output.isVisible():
            self.show_output()
        self._update_screen_info()

    def _update_screen_info(self):
        t = self._target()
        here = self.screen()
        visible = self.output.isVisible()
        self.btn_output.setText("Schowaj zegar" if visible else "Pokaż zegar na ekranie")
        if t is not None and here is not None and t.name() == here.name():
            text = ("Zegar zasłoni to okno (ten sam monitor). Esc na zegarze go chowa, "
                    "spacja i T działają dalej.")
        elif visible:
            text = "Zegar jest na pełnym ekranie na wybranym monitorze."
        else:
            text = "Zegar na pełnym ekranie na wybranym monitorze – w vMixie kluczuj kolor tła."
        self.lb_screen.setText(text)

    def _auto_show(self):
        """Przy starcie: zegar od razu na drugim monitorze (gdy jest)."""
        t = self._target()
        here = self.screen()
        if t is not None and (here is None or t.name() != here.name()):
            self.show_output()

    def show_output(self):
        t = self._target()
        if t is None:
            return
        place_fullscreen(self.output, t)
        log.info("Ekran zegara: %s", t.name())
        self._update_screen_info()

    def hide_output(self):
        self.output.hide()
        self._update_screen_info()
        self.activateWindow()

    def toggle_output(self):
        self.hide_output() if self.output.isVisible() else self.show_output()

    def closeEvent(self, e):
        self.output.close()
        super().closeEvent(e)


def main():
    from .log import setup_logging
    from .theme import apply_theme
    setup_logging()
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    if sys.platform == "win32":
        try:                                  # własna ikona na pasku zadań
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Galley.Zegar")
        except (OSError, AttributeError):
            pass
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setWindowIcon(utils.app_icon())
    app.setStyle("Fusion")
    apply_theme(app, "system")                # jasny / ciemny jak Windows
    w = ClockWindow()
    w.show()
    return app.exec()
