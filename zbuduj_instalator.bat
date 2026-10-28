@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GALLEY Zegar - budowanie instalatora

REM ==========================================================================
REM  Jeden plik do wszystkiego: instaluje (jesli trzeba) Pythona 3.12
REM  i Inno Setup, buduje program i tworzy instalator:
REM      instalator\GALLEY-Zegar-Setup.exe
REM  Wszystko instaluje sie tylko dla biezacego uzytkownika, bez admina.
REM ==========================================================================

set "PY_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"
set "INNO_URL=https://jrsoftware.org/download.php/is.exe"

echo.
echo ==============================================
echo    GALLEY Zegar - budowanie instalatora
echo ==============================================
echo.

REM ------------------------------------------------- Kompletnosc plikow
set "MISSING="
if not exist "zegar.py" set "MISSING=%MISSING% zegar.py"
if not exist "galley_zegar\app.py" set "MISSING=%MISSING% galley_zegar\(caly folder)"
if not exist "requirements.txt" set "MISSING=%MISSING% requirements.txt"
if not exist "zegar.ico" set "MISSING=%MISSING% zegar.ico"
if not exist "instalator.iss" set "MISSING=%MISSING% instalator.iss"
if defined MISSING goto :err_files

REM ---------------------------------------------------------------- Python
echo [1/4] Sprawdzam Pythona 3.12...
call :find_python
if defined PY goto :python_ok

echo       Brak Pythona 3.12 - instaluje...
where winget >nul 2>&1
if errorlevel 1 goto :python_download
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
call :find_python
if defined PY goto :python_ok

:python_download
echo       Pobieram instalator z python.org...
curl.exe -L --fail -o "%TEMP%\zegar-python.exe" "%PY_URL%"
if errorlevel 1 goto :err_download
"%TEMP%\zegar-python.exe" /quiet InstallAllUsers=0 InstallLauncherAllUsers=0 PrependPath=0 Include_test=0
del "%TEMP%\zegar-python.exe" >nul 2>&1
call :find_python
if not defined PY goto :err_python

:python_ok
echo       OK: %PY%
echo.

REM ------------------------------------------------------------ Inno Setup
echo [2/4] Sprawdzam Inno Setup...
call :find_iscc
if defined ISCC goto :inno_ok

echo       Brak Inno Setup - instaluje...
where winget >nul 2>&1
if errorlevel 1 goto :inno_download
winget install -e --id JRSoftware.InnoSetup --scope user --silent --accept-package-agreements --accept-source-agreements
call :find_iscc
if defined ISCC goto :inno_ok

:inno_download
echo       Pobieram instalator z jrsoftware.org...
curl.exe -L --fail -o "%TEMP%\zegar-inno.exe" "%INNO_URL%"
if errorlevel 1 goto :err_download
"%TEMP%\zegar-inno.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER
del "%TEMP%\zegar-inno.exe" >nul 2>&1
call :find_iscc
if not defined ISCC goto :err_inno

:inno_ok
echo       OK: %ISCC%
echo.

REM --------------------------------------------------------- Biblioteki
echo [3/4] Przygotowuje srodowisko i buduje program (kilka minut)...
if not exist "build-env\Scripts\python.exe" "%PY%" -m venv build-env
if not exist "build-env\Scripts\python.exe" goto :err_venv
set "VPY=%CD%\build-env\Scripts\python.exe"
"%VPY%" -m pip install --upgrade pip --quiet
"%VPY%" -m pip install --upgrade -r requirements.txt pyinstaller --quiet
if errorlevel 1 goto :err_pip
"%VPY%" -m PyInstaller --noconfirm --clean zegar.spec
if errorlevel 1 goto :err_build
echo.

REM ----------------------------------------------------------- Instalator
echo [4/4] Tworze instalator...
"%ISCC%" /Q instalator.iss
if errorlevel 1 goto :err_build

echo.
echo ==============================================
echo    GOTOWE: instalator\GALLEY-Zegar-Setup.exe
echo ==============================================
echo.
explorer "%CD%\instalator"
pause
exit /b 0

REM ======================================================== Funkcje pomocnicze
:find_python
set "PY="
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PY=%LocalAppData%\Programs\Python\Python312\python.exe"
if defined PY exit /b 0
if exist "%ProgramFiles%\Python312\python.exe" set "PY=%ProgramFiles%\Python312\python.exe"
if defined PY exit /b 0
for /f "delims=" %%i in ('py -3.12 -c "import sys;print(sys.executable)" 2^>nul') do set "PY=%%i"
exit /b 0

:find_iscc
set "ISCC="
for %%v in (6 7) do if exist "%LocalAppData%\Programs\Inno Setup %%v\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup %%v\ISCC.exe"
if defined ISCC exit /b 0
for %%v in (6 7) do if exist "%ProgramFiles(x86)%\Inno Setup %%v\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup %%v\ISCC.exe"
if defined ISCC exit /b 0
for %%v in (6 7) do if exist "%ProgramFiles%\Inno Setup %%v\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup %%v\ISCC.exe"
exit /b 0

REM ================================================================== Bledy
:err_files
echo.
echo BLAD: w folderze brakuje plikow:%MISSING%
echo Wszystkie pliki programu musza lezec w jednym folderze z tym skryptem.
goto :fail
:err_download
echo.
echo BLAD: nie udalo sie pobrac pliku. Sprawdz polaczenie z internetem.
goto :fail
:err_python
echo.
echo BLAD: Python 3.12 nie zainstalowal sie. Zainstaluj go recznie z python.org
echo (wersja 3.12, 64-bit) i uruchom ten plik ponownie.
goto :fail
:err_inno
echo.
echo BLAD: Inno Setup nie zainstalowal sie. Pobierz go recznie z
echo https://jrsoftware.org/isdl.php i uruchom ten plik ponownie.
goto :fail
:err_venv
echo.
echo BLAD: nie udalo sie utworzyc srodowiska Pythona (folder build-env).
goto :fail
:err_pip
echo.
echo BLAD: instalacja bibliotek nie powiodla sie. Sprawdz internet i sprobuj ponownie.
goto :fail
:err_build
echo.
echo BLAD: budowanie nie powiodlo sie. Sprawdz komunikaty powyzej.
goto :fail
:fail
echo.
pause
exit /b 1
