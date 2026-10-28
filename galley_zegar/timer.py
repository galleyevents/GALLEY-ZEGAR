"""Liczenie czasu wystąpienia - to samo co zegar w widoku prelegenta GALLEY Presentation Manager
(galley/slideshow.py: hms, timer_display, Stopwatch). Zmiany tu warto przenieść też do Presentera."""

from PySide6.QtCore import QElapsedTimer

TIMER_WARN_MS = 2 * 60 * 1000            # ostatnie 2 minuty na żółto


def hms(ms):
    s = int(ms) // 1000
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def timer_display(elapsed_ms, mode, limit_ms, overtime):
    """Co pokazuje zegar: (podpis, tekst, stan). Stan: "normal", "warn" (ostatnie 2 minuty),
    "over" (po czasie, na minusie - czerwony, mruga), "done" (czas minął, bez minusa - czerwone 00:00:00)."""
    if mode != "down":
        return "Czas wystąpienia", hms(elapsed_ms), "normal"
    left = limit_ms - elapsed_ms
    if left > 0:
        # w górę do pełnej sekundy: 14:59,4 pokazuje 15:00 jak zwykły minutnik
        shown = -(-left // 1000) * 1000
        return "Pozostało", hms(shown), ("warn" if left <= TIMER_WARN_MS else "normal")
    if not overtime:
        return "Czas minął", hms(0), "done"
    return "Po czasie", "−" + hms(-left), "over"


class Stopwatch:
    """Stoper z pauzą."""

    def __init__(self):
        self._acc = 0
        self._t = QElapsedTimer()
        self.running = False

    def start(self):
        if not self.running:
            self._t.start()
            self.running = True

    def pause(self):
        if self.running:
            self._acc += self._t.elapsed()
            self.running = False

    def reset(self):
        """Reset; jeśli stoper chodził, chodzi dalej."""
        self._acc = 0
        if self.running:
            self._t.start()

    def elapsed_ms(self):
        return self._acc + (self._t.elapsed() if self.running else 0)

    def adjust(self, ms):
        """Przesunięcie czasu (np. +1 min); nigdy poniżej zera."""
        self._acc = max(self._acc + ms, -(self._t.elapsed() if self.running else 0))
