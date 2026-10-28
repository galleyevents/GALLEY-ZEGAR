"""Punkt startowy GALLEY Zegar (z niego PyInstaller buduje GalleyZegar.exe): python zegar.py"""

if __name__ == "__main__":
    from galley_zegar.app import main
    raise SystemExit(main())
