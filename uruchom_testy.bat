@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GALLEY Zegar - testy

REM Uruchamia testy automatyczne (folder tests). Korzysta ze srodowiska
REM build-env, ktore tworzy zbuduj_instalator.bat - najpierw uruchom tamten.

if not exist "build-env\Scripts\python.exe" (
  echo Brak srodowiska build-env. Najpierw uruchom zbuduj_instalator.bat.
  pause
  exit /b 1
)
"build-env\Scripts\python.exe" -m pip install --quiet -r requirements-dev.txt
if errorlevel 1 goto :fail
"build-env\Scripts\python.exe" -m pytest tests -q
if errorlevel 1 goto :fail
echo.
echo WSZYSTKIE TESTY PRZESZLY.
pause
exit /b 0
:fail
echo.
echo NIEKTORE TESTY NIE PRZESZLY - szczegoly powyzej.
pause
exit /b 1
