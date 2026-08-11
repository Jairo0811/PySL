# Arquitectura de PySL

PySL es la plataforma de escritorio. **SL (Structured Language)** es el lenguaje educativo procesado por el núcleo y **Python** es el lenguaje de referencia utilizado por el conversor bidireccional y por la representación intermedia restringida del entorno de ejecución.

## Vista general

```mermaid
flowchart LR
    User["Usuario"] --> UI["PySide6 · UI / Dashboard"]
    UI --> Modules["Módulos funcionales"]

    Modules --> Editor["Editor e IDE de SL"]
    Modules --> Converter["Conversor SL ↔ Python"]
    Modules --> Learning["Ejemplos y utilidades educativas"]
    Modules --> Session["Sesión local"]

    Editor --> Language["language · Parser / Transpilador"]
    Converter --> Language
    Language --> Guard["Validación AST y límites"]
    Guard --> Worker["Proceso aislado"]
    Worker --> Runtime["runtime · Ejecución educativa"]

    Modules --> Core["core · Configuración / Servicios"]
    Core --> SQLite[("SQLite · pysl.db")]
    Core --> Files["Sistema de archivos / Recursos"]
    Core --> Logs["Logging y manejo de errores"]

    Package["PyInstaller"] --> UI
```

La interfaz y los módulos funcionales permanecen separados del núcleo del lenguaje. `language` puede analizar, convertir y validar código sin depender de PySide6 ni de SQLite; `core` concentra infraestructura local y el proceso aislado contiene la ejecución potencialmente no confiable.

## Responsabilidades

| Paquete | Responsabilidad |
|---|---|
| `core` | Configuración, rutas, sesión, SQLite, logging y errores globales |
| `language` | Parser/transpilador de SL, conversión SL ↔ Python, validación AST, aislamiento y límites |
| `modules` | Vistas y casos de uso agrupados por funcionalidad |
| `runtime` | Utilidades educativas y soporte de ejecución controlada |
| `ui` | Ventana principal, navegación y estilos comunes |

## Flujo de ejecución de SL

```mermaid
sequenceDiagram
    participant IDE as IDE de SL
    participant Worker as Worker Qt
    participant Parser as Transpilador
    participant Guard as Validador AST
    participant Child as Proceso aislado
    IDE->>Worker: código + entradas
    Worker->>Parser: transpilar SL
    Parser->>Guard: Python restringido
    Guard->>Child: programa validado
    Child-->>Worker: salida o error limitado
    Worker-->>IDE: resultado
```

El proceso hijo recibe únicamente el código Python restringido, las entradas y una estructura inmutable de límites. Su entorno no expone `__builtins__` generales. Las operaciones con potencial de crecimiento se redirigen a funciones acotadas y la comunicación regresa por una tubería de `multiprocessing`.

## Dependencias

- Las vistas dependen de servicios del mismo módulo y de contratos del núcleo.
- `language` no depende de PySide6 ni de SQLite, por lo que puede probarse aisladamente.
- `core.database` utiliza consultas parametrizadas y conexiones de vida corta.
- La composición de vistas ocurre en `DashboardView`; el punto de entrada configura Qt, logging y manejo global de errores.
- El proceso de ejecución aislado no obtiene acceso directo a la interfaz ni a la base de datos.

## Persistencia

La base `pysl.db` reside en una carpeta escribible por usuario:

- Windows: `%LOCALAPPDATA%\PySL`;
- macOS: `~/Library/Application Support/PySL`;
- Linux: `$XDG_DATA_HOME/PySL` o `~/.local/share/PySL`.

Los recursos empaquetados se resuelven desde el proyecto durante desarrollo y desde `_MEIPASS` al ejecutar el build de PyInstaller.

## Decisiones de alcance 1.x

- Arquitectura modular por funcionalidades, sin introducir un framework adicional.
- Conversión Python → SL basada en AST y limitada a equivalencias educativas seguras.
- Ejecución en proceso separado en lugar de hilo: un hilo no puede detener con seguridad un ciclo infinito de Python.
- Persistencia SQLite local, suficiente para un único usuario de escritorio.
- Separación explícita entre interfaz, núcleo del lenguaje, runtime e infraestructura local.
