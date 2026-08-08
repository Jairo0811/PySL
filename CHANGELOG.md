# Changelog

Todos los cambios relevantes de PySL se documentan en este archivo. El proyecto utiliza [versionado semántico](https://semver.org/lang/es/).

## 1.0.4 - 2026-08-08

### Interfaz y experiencia

- Elimina el módulo **Galería** de la navegación y del código fuente; el material histórico permanece preservado en `legacy/web-original/`.
- Implementa temas **Oscuro** y **Claro** funcionales en toda la aplicación.
- Aplica el cambio de tema y tamaño de fuente en tiempo real desde Configuración.
- Restaura automáticamente las preferencias visuales guardadas al iniciar PySL.
- Adapta la numeración de líneas y el resaltado de línea actual del editor al tema activo.
- Mantiene el **Menor número par** como laboratorio, preservando el ejercicio académico original sin duplicarlo como juego.
- Integra el **Ahorcado** original al sistema de estadísticas SQLite compartido por el Arcade PySL.

### Calidad

- Añade pruebas automatizadas para normalización de temas y límites del tamaño de fuente.
- Mantiene la configuración visual centralizada en `pysl.ui.styles` para evitar estilos duplicados.
- Actualiza README y documentación de versión para reflejar el alcance final simplificado.

## 1.0.3 - 2026-08-01

### Seguridad y estabilidad

- Ejecuta programas SL en un proceso aislado con límites de tiempo, pasos, ciclos, entrada, salida, AST, colecciones, enteros y memoria compatible.
- Impide sobrescribir nombres internos, usar atributos, imports o llamadas fuera del subconjunto autorizado.
- Valida expresiones de SL sin modificar palabras lógicas dentro de cadenas.
- Verifica la credencial demostrativa mediante PBKDF2 en lugar de comparar texto plano.
- Endurece SQLite con tiempo de espera, `busy_timeout`, WAL, columnas explícitas y validación de datos.
- Añade registro rotativo y manejo global de errores de la aplicación.

### Conversión y experiencia

- Sustituye el conversor basado en líneas por análisis AST seguro para Python → SL.
- Corrige conversión de bloques anidados, `else`, funciones, ciclos y expresiones lógicas.
- Ejecuta el runtime desde un worker para no bloquear la interfaz de Qt.
- Normaliza toda la interfaz y documentación a **SL → Python** y **Python → SL**.

### Calidad y distribución

- Amplía la suite a 31 pruebas automatizadas.
- Configura Ruff, formato reproducible y versión centralizada.
- Añade CI para Python 3.12/3.13, capturas reproducibles y build verificado en Windows.
- Añade publicación automática de GitHub Releases con ejecutable Windows.
- Incorpora ejemplos, documentación de arquitectura, seguridad y distribución.

## 1.0.2 - 2026-07-14

- Rediseñó la pantalla Acerca de PySL y centralizó la información académica.
- Renovó el dashboard con accesos rápidos y estadísticas reales de SQLite.
- Movió los datos de usuario a una ruta escribible independiente de la instalación.
- Añadió compatibilidad de recursos y script de compilación para PyInstaller.
- Actualizó créditos, versión y documentación.

## 1.0.1 - 2026-07-14

- Corrigió el resaltado de línea actual para PySide6 6.11.
- Añadió el icono de Windows y mejoró el script de compilación.
- Actualizó la presentación académica de la plataforma.

## 1.0.0 - 2026-07-14

- Publicó el IDE para archivos `.pysl`, runtime, conversor, curso, laboratorio y juegos.
- Incorporó persistencia SQLite, documentación y preparación de distribución Windows.
