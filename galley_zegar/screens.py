"""Skopiowane z GALLEY Presentation Manager (galley/screens.py). Monitory: kolejność, opisy, pełny ekran na wybranym monitorze, plansze z numerami."""

from PySide6.QtCore import QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .theme import ACCENT, MUTED, TEXT, font


# „Slajdy na: Brak – tylko widok prelegenta” (jeden monitor, do testów)
NO_AUDIENCE = "__brak__"


def sorted_screens():
    """Monitory od lewej do prawej (tak jak stoją na biurku w ustawieniach)."""
    return sorted(QGuiApplication.screens(),
                  key=lambda s: (s.geometry().x(), s.geometry().y()))


def screen_resolution(screen):
    geo, dpr = screen.geometry(), screen.devicePixelRatio()
    return round(geo.width() * dpr), round(geo.height() * dpr)


def screen_label(number, screen):
    """Krótki opis do listy: numer (jak w „Pokaż numery”), rozdzielczość."""
    w, h = screen_resolution(screen)
    label = f"Ekran {number} · {w}×{h}"
    if screen.name() == QGuiApplication.primaryScreen().name():
        label += " · główny"
    return label


def screen_details(number, screen):
    """Pełny opis (model monitora) do podpowiedzi i plansz z numerami."""
    w, h = screen_resolution(screen)
    model = (screen.model() or "").strip() or (screen.manufacturer() or "").strip()
    return f"{model}  ·  {w}×{h}" if model else f"{w}×{h}"


def place_fullscreen(w, screen):
    """Pełny ekran na konkretnym monitorze (działa też na Windows)."""
    if w.isFullScreen():
        w.showNormal()
    geo = screen.geometry()
    w.setGeometry(geo)
    w.show()
    handle = w.windowHandle()
    if handle is not None and handle.screen() is not screen:
        handle.setScreen(screen)
    w.setGeometry(geo)
    w.showFullScreen()


class ScreenBadge(QWidget):
    """Duży numer wyświetlany na chwilę na każdym monitorze."""

    def __init__(self, screen, number, text):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint
                         | Qt.WindowStaysOnTopHint)
        self.number, self.text = number, text
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_DeleteOnClose)
        geo = screen.geometry()
        w, h = 460, 320
        self.setGeometry(geo.x() + (geo.width() - w) // 2,
                         geo.y() + (geo.height() - h) // 2, w, h)
        QTimer.singleShot(3000, self.close)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(22, 24, 29, 235))
        p.setPen(QPen(ACCENT, 4))
        p.drawRoundedRect(QRectF(self.rect()).adjusted(2, 2, -2, -2), 24, 24)
        p.setPen(TEXT)
        p.setFont(font(170, True))
        p.drawText(QRectF(0, 10, self.width(), 220), Qt.AlignCenter, str(self.number))
        p.setFont(font(22))
        p.setPen(MUTED)
        p.drawText(QRectF(20, 230, self.width() - 40, 70),
                   Qt.AlignCenter | Qt.TextWordWrap, self.text)
