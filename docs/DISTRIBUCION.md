# Distribución de PySL para Windows

## Requisitos

- Windows 10 u 11 de 64 bits;
- Python 3.12 o 3.13 para generar el build;
- PowerShell 7 o Windows PowerShell con ejecución permitida para el script local.

## Build reproducible

```powershell
py -3.13 -m venv .venv
Unblock-File .\scripts\build_windows.ps1
.\scripts\build_windows.ps1
```

El script:

1. instala `.[dev,build]`;
2. ejecuta Pytest;
3. ejecuta `ruff check` y `ruff format --check`;
4. valida sintaxis con `compileall`;
5. genera un build `onedir` y `windowed` con PyInstaller;
6. verifica que exista `dist\PySL\PySL.exe`.

## Versionado y release

La versión se define una sola vez en `src/pysl/__init__.py` y `pyproject.toml` la obtiene dinámicamente. Para publicar una versión estable:

1. actualizar `__version__`, README y CHANGELOG;
2. fusionar CI en verde a `main`;
3. crear un tag anotado `vMAJOR.MINOR.PATCH`;
4. enviar el tag a GitHub.

El workflow `release.yml` valida que el tag coincida con la versión, repite las pruebas y el build, comprime el resultado y publica `PySL-Windows-x64.zip` en GitHub Releases.

## Datos de usuario

El ejecutable no escribe la base de datos dentro de `dist`. En Windows utiliza `%LOCALAPPDATA%\PySL`, por lo que actualizar o reemplazar la carpeta de la aplicación no elimina el progreso.
