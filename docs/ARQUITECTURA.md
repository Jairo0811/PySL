# Arquitectura de PySL

PySL usa una arquitectura modular por funcionalidades:

- `core`: configuración, sesión y SQLite.
- `language`: transpilador y ejecutor restringido.
- `runtime`: API educativa compatible con Python.
- `modules`: interfaz y casos de uso por módulo.
- `tests`: pruebas unitarias del núcleo.
- `legacy`: proyecto web original preservado.

El código PySL se transpila a un subconjunto de Python, se valida mediante AST y se ejecuta sin acceso a `__builtins__` generales.
