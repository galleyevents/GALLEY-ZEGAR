# GALLEY Zegar

Program dla Windows: **zegar czasu wystąpienia na pełnym ekranie** na jednolitym tle – domyślnie **zielonym do kluczowania** w vMixie (Chroma Key). Osobny program firmy GALLEY, zbudowany na bazie zegara z GALLEY Presentation Manager (liczy tak samo).

## Jak działa

- **Pierwszy ekran – sterowanie:** podgląd tego, co widać na ekranie zegara, przyciski **Start / Pauza**, **Resetuj zegar**, **−1 min / +1 min**. Zegar **liczy w górę** albo **odlicza** czas wystąpienia (np. 15 min); po czasie może liczyć dalej na minusie.
- **Gotowe czasy (od 1.1):** przyciski **5 / 10 / 15 / 30 min** – jedno kliknięcie ustawia odliczanie od tego czasu i zatrzymuje zegar na pełnym czasie (potem Start). **+ Własny…** dodaje własny czas (np. 20 albo 45 min, zapamiętany); własny usuwa się prawym przyciskiem. Przyciski sterowania czasem są duże i czytelne.
- **Wygląd:** tło (zielone albo niebieskie – oba do kluczowania – czarne albo dowolny kolor), kolor cyfr (białe, czarne, złote albo dowolny), wielkość cyfr, ostrzeżenia (ostatnie 2 minuty na żółto, po czasie na czerwono i mruga), podpis nad zegarem („Pozostało”, „Po czasie”). Ustawienia są zapamiętywane.
- **Drugi ekran – zegar:** przy starcie zegar sam pojawia się na pełnym ekranie na drugim monitorze (wybór monitora w części „Ekran zegara”). **Schowaj zegar / Pokaż zegar na ekranie** (F11). Przy jednym monitorze zegar zasłoni okno sterowania – **Esc** na zegarze go chowa.
- **Klawisze:** spacja – start / pauza, T – resetuj zegar, + / − – minuta, F11 – ekran zegara.
- Mruganie po czasie to przyciemnienie cyfr, nie przezroczystość (półprzezroczyste cyfry mieszałyby się z zielonym tłem przy kluczowaniu).
- Dziennik: `%LOCALAPPDATA%\GALLEY Zegar\zegar.log`.

## Instalacja

Zakładka **Releases** → `GALLEY-Zegar-X.Y-Setup.exe`. Instaluje się bez uprawnień administratora, skrót **GALLEY Zegar** w menu Start. Niezależny od GALLEY Presentation Manager (własna instalacja, własne ustawienia).

## Dla programisty

```
pip install -r requirements-dev.txt
python zegar.py                 # uruchomienie ze źródeł
python -m pytest tests -q       # testy bez monitora (Qt offscreen, dwa wirtualne ekrany)
zbuduj_instalator.bat           # Windows: Python, Inno Setup, PyInstaller -> instalator\GALLEY-Zegar-Setup.exe
```

Wydanie: podbić numer w `galley_zegar/__init__.py` i `instalator.iss`, wysłać zmiany, potem Actions → „Testy i instalator” → Run workflow z polem „wydanie” (np. `1.1`).

| Plik | Zawartość |
|---|---|
| `zegar.py` | punkt startowy |
| `galley_zegar/app.py` | okno sterowania (`ClockWindow`), ekran zegara (`ClockView`), rysowanie (`paint_clock`), stan (`ClockModel`) |
| `galley_zegar/timer.py` | liczenie czasu (jak w Presenterze: `Stopwatch`, `timer_display`) |
| `galley_zegar/theme.py`, `screens.py` | wygląd i monitory – skopiowane z GALLEY Presentation Manager |
| `zegar.spec`, `instalator.iss` | budowanie `GalleyZegar.exe` i instalatora |
