# -*- mode: python ; coding: utf-8 -*-
# GALLEY Zegar - przepis budowania .exe (PyInstaller, onedir):
#     python -m PyInstaller --noconfirm --clean zegar.spec
# Tylko to, czego potrzebuje zegar (Qt Widgets) - bez multimediów, sieci i silnika PDF Presentera.

a = Analysis(
    ['zegar.py'],
    datas=[('zegar.ico', '.')],
    excludes=['PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtWebEngineCore',
              'PySide6.QtWebEngineWidgets', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.Qt3DCore',
              'PySide6.QtCharts', 'PySide6.QtDataVisualization', 'PySide6.QtPdf', 'tkinter'],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GalleyZegar',
    console=False,
    icon=['zegar.ico'],
    manifest='zegar.manifest',                   # ostre wyświetlanie przy skalowaniu ekranu
)
coll = COLLECT(exe, a.binaries, a.datas, name='GalleyZegar')
