"""Wygląd: kolory marki, motyw jasny/ciemny (QSS), ikony rysowane w kodzie, czcionki.

Skopiowane z GALLEY Presentation Manager (galley/theme.py) - zegar wygląda jak Presenter."""

import os
import tempfile

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QIcon, QPainter, QPen, QPixmap



FONT = "Segoe UI"


# Kolory widoku prelegenta (ciemny, żeby nie oślepiać w zaciemnionej sali)
BG = QColor("#101215")


PANEL = QColor("#1A1D22")


TEXT = QColor("#ECEEF1")


MUTED = QColor("#8A929E")


ACCENT = QColor("#D9A441")     # mosiądz: akcent marki


WARN = QColor("#E7B95C")


ALERT = QColor("#E9634F")


UI_FONT = '"Segoe UI Variable Text", "Segoe UI", "Helvetica Neue", Arial, sans-serif'


# Paleta oparta na logo: atrament (czerń) i papier (biel) + jeden akcent,
# mosiądz, jak na przyrządach nawigacyjnych. Akcent oznacza zawsze to samo:
# „tu jesteś / to jest następne / tu jest film”.
THEMES = {
    "light": {
        "canvas": "#EEF0F3", "surface": "#FFFFFF", "surface2": "#F6F7F9",
        "line": "#DCE0E5", "ink": "#15181D", "ink2": "#4B525C", "ink3": "#7B838E",
        "brass": "#B8862B", "brass_soft": "#F6EDDC", "brass_text": "#8A6215",
        "preview": "#E1E4E8", "primary_hover": "#2B3038", "on_primary": "#FFFFFF",
        "brass_hover": "#C99636", "on_brass": "#15181D",
        "ok": "#2F8F5B", "danger": "#C2412D", "danger_soft": "#FBEAE6",
    },
    "dark": {
        "canvas": "#0F1114", "surface": "#171A1F", "surface2": "#1E2228",
        "line": "#2A2F37", "ink": "#ECEEF1", "ink2": "#B5BBC4", "ink3": "#828A96",
        "brass": "#D9A441", "brass_soft": "#2B2416", "brass_text": "#E7B95C",
        "preview": "#0A0C0E", "primary_hover": "#FFFFFF", "on_primary": "#0F1114",
        "brass_hover": "#E7B95C", "on_brass": "#15181D",
        "ok": "#4CB57E", "danger": "#E26A55", "danger_soft": "#2E1B17",
    },
}


T = dict(THEMES["light"], name="light")   # bieżący motyw (ustawia apply_theme)


def C(name):
    return QColor(T[name])


def build_qss(t):
    return f"""
QWidget {{ font-family: {UI_FONT}; font-size: 13px; color: {t['ink']}; }}
QMainWindow, #Canvas {{ background: {t['canvas']}; }}
#Header {{ background: {t['surface']}; border-bottom: 2px solid {t['brass']}; }}
#Sidebar {{ background: {t['surface']}; border-right: 1px solid {t['line']}; }}
#ThumbList {{ background: {t['surface2']}; border: none; border-top: 1px solid {t['line']}; }}
#StartPage {{ background: {t['canvas']}; }}
#FitScroll, #FitScroll > QWidget, #ScrollBody {{ background: transparent; }}
#Title {{ font-size: 15px; font-weight: 600; }}
#BigTitle {{ font-size: 26px; font-weight: 600; }}
#Section {{ color: {t['ink2']}; font-size: 12px; font-weight: 600; }}
#Caption {{ color: {t['ink3']}; font-size: 11px; font-weight: 600; }}
#PanelHeader {{ border: none; border-bottom: 2px solid {t['brass']}; }}
#PanelTitle {{ font-size: 18px; font-weight: 600; }}
#Wordmark {{ font-size: 30px; font-weight: 600; }}
#Muted {{ color: {t['ink3']}; }}
#Warn {{ color: {t['danger']}; font-weight: 600; }}
#FolderName {{ font-size: 14px; font-weight: 600; }}

QPushButton {{ background: {t['surface']}; border: 1px solid {t['line']}; border-radius: 6px;
              padding: 7px 14px; }}
QPushButton:hover {{ background: {t['surface2']}; border-color: {t['ink3']}; }}
QPushButton:focus {{ border-color: {t['brass']}; outline: none; }}
QPushButton:disabled {{ color: {t['ink3']}; background: {t['surface2']}; border-color: {t['line']}; }}
QPushButton#Primary {{ background: {t['brass']}; color: {t['on_brass']}; border: 1px solid {t['brass']};
                      font-weight: 600; padding: 8px 18px; }}
QPushButton#Primary:hover {{ background: {t['brass_hover']}; border-color: {t['brass_hover']}; }}
QPushButton#Primary:focus {{ border: 2px solid {t['ink']}; }}
QPushButton#Primary:disabled {{ background: {t['line']}; border-color: {t['line']}; color: {t['ink3']}; }}
QPushButton#Ghost {{ background: transparent; border: 1px solid transparent; padding: 5px 8px; }}
QPushButton#Ghost:hover {{ background: {t['surface2']}; border-color: {t['line']}; }}
QPushButton#Chip {{ background: {t['surface2']}; border: 1px solid {t['line']}; border-radius: 16px;
                   padding: 6px 14px; text-align: left; }}
QPushButton#Chip:hover {{ border-color: {t['brass']}; }}
#Header QPushButton {{ font-size: 14px; min-height: 30px; padding: 7px 16px; }}
#Header QPushButton#Primary {{ font-size: 16px; min-height: 34px; padding: 9px 26px; }}
#Header QPushButton#HeaderChip {{ background: {t['surface2']}; border: 1px solid {t['line']}; border-radius: 18px;
                         padding: 7px 16px; color: {t['ink2']}; }}
#Header QPushButton#HeaderChip:hover {{ border-color: {t['brass']}; color: {t['ink']}; }}

QLineEdit {{ background: {t['surface2']}; border: 1px solid {t['line']}; border-radius: 6px;
            padding: 6px 8px; selection-background-color: {t['brass']}; }}
QLineEdit:focus {{ border-color: {t['brass']}; background: {t['surface']}; }}
QComboBox {{ background: {t['surface']}; border: 1px solid {t['line']}; border-radius: 6px;
            padding: 6px 10px; min-height: 18px; }}
QComboBox:hover, QComboBox:focus {{ border-color: {t['brass']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{ image: url("{t['arrow_png']}"); width: 12px; height: 12px; }}
QComboBox QAbstractItemView {{ background: {t['surface']}; border: 1px solid {t['line']};
                              selection-background-color: {t['brass_soft']}; selection-color: {t['ink']};
                              outline: 0; padding: 4px; }}

QTreeWidget, QListWidget {{ background: transparent; border: none; outline: 0; }}
QTreeWidget::item {{ padding: 5px 4px; border-radius: 5px; }}
QTreeWidget::item:hover {{ background: {t['surface2']}; }}
QTreeWidget::item:selected {{ background: {t['brass_soft']}; color: {t['ink']}; }}
QTreeWidget {{ selection-background-color: transparent; show-decoration-selected: 0; }}
QTreeWidget::branch, QTreeWidget::branch:selected, QTreeWidget::branch:hover {{ background: transparent; }}

QMenuBar {{ background: {t['surface']}; border-bottom: 1px solid {t['line']}; padding: 2px 4px; }}
QMenuBar::item {{ padding: 4px 10px; border-radius: 5px; background: transparent; }}
QMenuBar::item:selected {{ background: {t['surface2']}; }}
QMenu {{ background: {t['surface']}; border: 1px solid {t['line']}; padding: 5px; }}
QMenu::item {{ padding: 6px 26px 6px 14px; border-radius: 5px; }}
QMenu::item:selected {{ background: {t['brass_soft']}; color: {t['ink']}; }}
QMenu::item:disabled {{ color: {t['ink3']}; }}
QMenu::separator {{ height: 1px; background: {t['line']}; margin: 5px 6px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {t['line']}; border-radius: 3px; min-height: 32px; }}
QScrollBar::handle:vertical:hover {{ background: {t['ink3']}; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {t['line']}; border-radius: 3px; min-width: 32px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QSplitter::handle {{ background: {t['line']}; }}
QToolTip {{ background: {t['ink']}; color: {t['on_primary']}; border: none; padding: 5px 8px; }}

#Card {{ background: {t['surface']}; border: 1px solid {t['line']}; border-radius: 10px; }}
#Card:hover {{ border-color: {t['brass']}; }}
#NextCard {{ background: {t['brass_soft']}; border: 1px solid {t['brass']}; border-radius: 8px; }}
#NextCard:hover {{ border-width: 2px; }}
#NextCardWarn {{ background: {t['danger_soft']}; border: 1px solid {t['danger']}; border-radius: 8px; }}
#NextCardWarn:hover {{ border-width: 2px; }}
#SideTabs::pane {{ border: none; border-top: 1px solid {t['line']}; }}
#SideTabs QTabBar::tab {{ background: transparent; color: {t['ink2']}; padding: 6px 12px;
    border: none; border-bottom: 2px solid transparent; font-weight: 600; }}
#SideTabs QTabBar::tab:selected {{ color: {t['ink']}; border-bottom-color: {t['brass']}; }}
#Popup {{ background: {t['surface']}; border: 1px solid {t['line']}; border-radius: 10px; }}
QMessageBox {{ background: {t['surface']}; }}
"""


def resolve_theme(mode):
    if mode in ("light", "dark"):
        return mode
    try:
        scheme = QGuiApplication.styleHints().colorScheme()
        return "dark" if scheme == Qt.ColorScheme.Dark else "light"
    except AttributeError:            # Qt starsze niż 6.5: brak informacji o motywie
        return "light"


def apply_theme(app, mode):
    """mode: "system" | "light" | "dark". Zwraca użyty wariant."""
    name = resolve_theme(mode)
    T.clear()
    T.update(THEMES[name])
    T["name"] = name
    T["arrow_png"] = _arrow_png(T["ink2"])
    from PySide6.QtGui import QPalette
    pal = QPalette()
    for role, key in ((QPalette.Window, "canvas"), (QPalette.Base, "surface"),
                      (QPalette.AlternateBase, "surface2"), (QPalette.Button, "surface"),
                      (QPalette.Text, "ink"), (QPalette.WindowText, "ink"),
                      (QPalette.ButtonText, "ink"), (QPalette.Highlight, "brass"),
                      (QPalette.PlaceholderText, "ink3"), (QPalette.ToolTipBase, "ink"),
                      (QPalette.ToolTipText, "on_primary")):
        pal.setColor(role, QColor(T[key]))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.Disabled, QPalette.Text, QColor(T["ink3"]))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(T["ink3"]))
    app.setPalette(pal)
    app.setStyleSheet(build_qss(T))
    return name


def _arrow_png(color):
    """Strzałka listy rozwijanej jako plik PNG (QSS potrzebuje ścieżki)."""
    from PySide6.QtGui import QPainterPath
    folder = os.path.join(tempfile.gettempdir(), "galley_ui")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"arrow_{color.strip('#')}.png").replace("\\", "/")
    if not os.path.isfile(path):
        pm = QPixmap(24, 24)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(color), 2.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        pp = QPainterPath()
        pp.moveTo(6, 9); pp.lineTo(12, 15); pp.lineTo(18, 9)
        p.drawPath(pp)
        p.end()
        pm.save(path)
    return path


def make_icon(name, color=None, size=20):
    """Proste ikony liniowe rysowane w kodzie (spójne w obu motywach)."""
    from PySide6.QtGui import QPainterPath
    color = QColor(color or T["ink2"])
    dpr = 2
    pm = QPixmap(size * dpr, size * dpr)
    pm.fill(Qt.transparent)
    pm.setDevicePixelRatio(dpr)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(size / 24, size / 24)
    pen = QPen(color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    if name == "file":
        path.moveTo(6, 3); path.lineTo(14, 3); path.lineTo(19, 8); path.lineTo(19, 21)
        path.lineTo(6, 21); path.closeSubpath()
        path.moveTo(14, 3); path.lineTo(14, 8); path.lineTo(19, 8)
        p.drawPath(path)
        p.drawLine(9, 13, 16, 13); p.drawLine(9, 16.5, 14, 16.5)
    elif name == "film":
        p.drawRoundedRect(QRectF(3, 5, 18, 14), 3, 3)
        tri = QPainterPath(); tri.moveTo(10, 9); tri.lineTo(15.5, 12); tri.lineTo(10, 15); tri.closeSubpath()
        p.setBrush(color); p.drawPath(tri)
    elif name == "folder":
        path.moveTo(3, 7); path.lineTo(3, 18.5); path.lineTo(21, 18.5); path.lineTo(21, 8.5)
        path.lineTo(11.5, 8.5); path.lineTo(9.5, 5.5); path.lineTo(3, 5.5); path.closeSubpath()
        p.drawPath(path)
    elif name == "check":
        p.setPen(QPen(color, 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path.moveTo(5, 12.5); path.lineTo(10, 17); path.lineTo(19, 7)
        p.drawPath(path)
    elif name == "current":
        p.setPen(Qt.NoPen); p.setBrush(color)
        tri = QPainterPath(); tri.moveTo(8, 5); tri.lineTo(19, 12); tri.lineTo(8, 19); tri.closeSubpath()
        p.drawPath(tri)
    elif name == "pause":
        p.setPen(Qt.NoPen); p.setBrush(color)
        p.drawRoundedRect(QRectF(6.5, 5, 4, 14), 1, 1); p.drawRoundedRect(QRectF(13.5, 5, 4, 14), 1, 1)
    elif name == "play":
        p.setPen(Qt.NoPen); p.setBrush(color)
        tri = QPainterPath(); tri.moveTo(7, 4.5); tri.lineTo(19.5, 12); tri.lineTo(7, 19.5); tri.closeSubpath()
        p.drawPath(tri)
    elif name == "phone":
        p.drawRoundedRect(QRectF(7, 2.5, 10, 19), 2.5, 2.5)
        p.drawLine(10.5, 18.5, 13.5, 18.5)
    elif name == "monitor":
        p.drawRoundedRect(QRectF(3, 4, 18, 12), 2, 2)
        p.drawLine(12, 16, 12, 20); p.drawLine(8, 20, 16, 20)
    elif name == "refresh":
        p.drawArc(QRectF(5, 5, 14, 14), 30 * 16, 290 * 16)
        path.moveTo(19.5, 4.5); path.lineTo(19, 9.5); path.lineTo(14.2, 8.4)
        p.drawPath(path)
    elif name == "search":
        p.drawEllipse(QRectF(4, 4, 12, 12)); p.drawLine(14.5, 14.5, 20, 20)
    elif name == "open":
        path.moveTo(3, 7); path.lineTo(3, 18.5); path.lineTo(17.5, 18.5); path.lineTo(21, 11)
        path.lineTo(7, 11); path.lineTo(3, 18.5)
        path.moveTo(3, 7); path.lineTo(3, 5.5); path.lineTo(9.5, 5.5); path.lineTo(11.5, 8.5)
        path.lineTo(18, 8.5); path.lineTo(18, 11)
        p.drawPath(path)
    elif name == "arrow":
        p.drawLine(5, 12, 19, 12); path.moveTo(13, 6); path.lineTo(19, 12); path.lineTo(13, 18)
        p.drawPath(path)
    elif name == "timer":
        p.drawEllipse(QRectF(5, 6, 14, 14)); p.drawLine(12, 13, 12, 9.5); p.drawLine(12, 13, 14.5, 14.5)
        p.drawLine(10, 3, 14, 3)
    elif name == "close":
        p.drawLine(6, 6, 18, 18); p.drawLine(18, 6, 6, 18)
    elif name == "list":                 # 3.13: kolejka pokazu (lista z punktami)
        for y in (6, 12, 18):
            p.drawLine(9, y, 20, y)
        p.setPen(Qt.NoPen); p.setBrush(color)
        for y in (6, 12, 18):
            p.drawEllipse(QRectF(3.5, y - 1.6, 3.2, 3.2))
    p.end()
    return QIcon(pm)


def font(px, bold=False):
    f = QFont(FONT)
    f.setPixelSize(max(8, int(px)))
    f.setBold(bold)
    return f


def fit_font_size(p, text, rect, bold=False, height_ratio=0.78):
    """Największa czcionka, przy której tekst mieści się w prostokącie."""
    p.setFont(font(100, bold))
    w100 = max(1, p.fontMetrics().horizontalAdvance(text))
    return max(8.0, min(rect.height() * height_ratio, 100 * rect.width() * 0.97 / w100))
