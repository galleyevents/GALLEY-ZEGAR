# CLAUDE.md: GALLEY Zegar

Osobny program firmy GALLEY (obsługa techniczna konferencji: vMix + laptopy): zegar czasu wystąpienia na pełnym
ekranie na jednolitym tle do kluczowania. Zbudowany na bazie zegara z repozytorium
`galleyevents/GALLEY_PDF_PRESENTER` (GALLEY Presentation Manager). Decyzja właściciela (28.10.2026): OSOBNY program
z własnym instalatorem i repozytorium - NIE tryb Presentera (próba jako `--zegar` w Presenterze, 3.14-beta.5,
została wycofana).

Aktualna wersja: **1.2** (`galley_zegar/__init__.py` `APP_VERSION` i `#define AppVersion` w `instalator.iss` - zawsze obie).

## Język i styl

- Interfejs, komentarze, README i rozmowa z właścicielem: **po polsku**. Właściciel nie jest programistą:
  konkretnie, bez żargonu, co się zmieniło i jak to sprawdzić.
- Pisownia jak w Presenterze: wtrącenia półpauzą „ – ”, „Czas wystąpienia”, „Resetuj zegar”.
- Każda wersja: podbić numer w obu miejscach, dopisać zmiany do `README.md`. Nowa funkcja = nowy test w `tests/`.

## Uruchamianie, testy, budowanie

```
pip install -r requirements-dev.txt
python zegar.py
python -m pytest tests -q        # Qt offscreen, dwa wirtualne ekrany 1920×1080 (LAPTOP + PROJEKTOR), osobne ustawienia
zbuduj_instalator.bat            # Windows
```

GitHub Actions (`.github/workflows/build.yml`): push = testy na Linuksie (darmowy plan: minuty Windows liczone 2×);
ręcznie z polem „wydanie” = budowanie na Windows + wydanie (Release) `GALLEY-Zegar-X.Y-Setup.exe`. BEZ artefaktów:
miejsce na pliki z Actions jest wspólne dla konta (0,5 GB) i bywa pełne przez Presentera - wydania się nie liczą.
Środowisko w chmurze nie wysyła tagów - wydanie tworzy przepływ (`gh release create`).

## Zasady i pułapki

- **Instalator**: `AppId` w `instalator.iss` NIE zmieniać (aktualizacja w miejscu); inny niż Presentera. Plik `.iss`
  UTF-8 z BOM, CRLF. Exe: `GalleyZegar.exe`, folder `{autopf}\GALLEY Zegar`, bez admina.
- **Ustawienia**: `QSettings("GALLEY", "Zegar")` (`utils.SETTINGS_ORG` / `SETTINGS_APP`; testy podmieniają ORG).
  Nazwy NIE zmieniać - aktualizacja zgubiłaby ustawienia.
- **Liczenie** (`timer.py`) = kopia z Presentera (`galley/slideshow.py`): żółty w ostatnich 2 min, po czasie minus na
  czerwono i mruga; poprawki warto przenosić w obie strony.
- **Kluczowanie**: mruganie BEZ przezroczystości (`clock_color` -> `darker`); kolory ostrzeżeń bez zieleni; tło
  domyślne `#00B140`. Podgląd i ekran zegara rysuje ta sama `paint_clock` (podgląd = wyjście, tylko mniejszy).
- **Monitory**: przy starcie zegar sam na pierwszym monitorze innym niż okno sterowania (`_auto_show`); zapamiętany
  monitor po nazwie Qt. Esc na ekranie zegara chowa go (gdy zasłania sterowanie). Do sprawdzenia na sprzęcie:
  skalowanie 125 / 150 %, kluczowanie w vMixie (krawędzie cyfr).
- **Presety czasu (1.1, prośba właściciela)**: wbudowane `BUILTIN_PRESETS` (5, 10, 15, 30) + własne w ustawieniu
  `presets` („20,45”; `load_custom_presets` / `save_custom_presets`, bez powtórek i wbudowanych). Klik = odliczanie od
  tego czasu, zegar ZATRZYMANY na pełnym czasie (`apply_preset`) - operator klika Start. Własny usuwa prawy przycisk.
  Przebudowa siatki (`_rebuild_presets`): wyjęty przycisk `hide()` + `setParent(None)` przed `deleteLater` - inaczej
  leżał na podglądzie. Duże przyciski: `clock_qss` (#BigStart, #Big, #Preset, #PresetAdd) na oknie sterowania.
- **Koniec czasu (1.2, prośba właściciela)**: ustawienia `warn_min` (0-60, domyślnie 2; 0 = bez końcówki),
  `warn_color` (domyślnie `WARN` żółty), `over_color` (domyślnie `OVER` czerwony; też stan „done” bez minusa).
  `timer_display(..., warn_ms)`, `clock_color` czyta kolory z `opt`. Wybór kolorów jak tło / cyfry (`WARN_COLORS`,
  `OVER_COLORS` + „Inny kolor…”); aktywne tylko przy odliczaniu z włączoną zmianą koloru (`_enable_controls`).
- `theme.py` i `screens.py` skopiowane z Presentera - wygląd ma zostać spójny z Presenterem.
- Błędy do dziennika (`from .log import log`), szerokie `except` tylko świadomie.
