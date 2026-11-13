# Changelog

Todos los cambios relevantes de PySL se documentan en este archivo. El proyecto utiliza [versionado semántico](https://semver.org/lang/es/).

## 1.0.5 - 2026-11-13

Última versión funcional de la línea 1.x: a partir de aquí solo se aceptan correcciones de errores y de seguridad.

### Lenguaje y runtime

- Los errores de ejecución se muestran **en español** y con la **línea SL** donde ocurrieron (división entre cero, índice fuera de rango, variable no definida, tipos incompatibles, conversión inválida, recursión, límites de recursos).
- Corrige `int("abc")`, que se reportaba como "El runtime rechazó el programa" en lugar de un error de ejecución normal.
- `imprimir()` sin argumentos imprime una línea en blanco (antes fallaba).
- Los comentarios con `#` al final de cualquier instrucción (`imprimir`, `leer`, `si`, `finsi`, `fin`…) ahora se aceptan; antes solo funcionaban en asignaciones. `//` sigue siendo división entera salvo al inicio de línea.
- Usar una palabra reservada de Python (`class`, `import`, `lambda`…) como nombre produce un error claro con su línea.
- El conversor Python → SL genera límites legibles: `range(1, 4)` ahora da `hasta 3` en lugar de `hasta (4) - 1`.

### Interfaz

- El IDE resalta la línea con error, muestra el nombre del archivo con marca de cambios sin guardar y pide confirmación antes de descartar cambios al crear/abrir, cerrar sesión o cerrar la aplicación.
- Corrige **Abrir**: un archivo ilegible o que no es UTF-8 ya no queda como archivo actual (riesgo de sobrescribirlo al guardar) ni provoca el diálogo de error global.
- Añade atajos: Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+Mayús+S, F5 y Ctrl+Enter.
- Inicio refresca las estadísticas al mostrarse y el laboratorio **Menor número par** ahora registra el progreso (antes "Laboratorios completados" siempre mostraba 0).
- Configuración revierte la vista previa si se sale sin guardar.
- El resaltador distingue comentarios, cadenas con comilla simple y división entera.
- Corrige fondos oscuros detrás de las etiquetas dentro de tarjetas y la fuente monoespaciada del Ahorcado fuera de Windows.
- El curso incluye ejemplos ejecutables en las seis lecciones y la documentación integrada cubre operadores, vectores, funciones y atajos.

### Pulido final

- Barra lateral compacta (todas las secciones caben en 1100×700 sin desplazamiento), páginas de Inicio y Laboratorio con desplazamiento en ventanas pequeñas, Configuración alineada y Acerca de legible en ambos temas.
- Inicio: héroe sin logo duplicado, estadísticas y accesos rápidos con jerarquía y proporciones consistentes.
- Acceso: leyenda "Cuenta académica de demostración · sesión local" y eslogan en español natural.
- Convertidor: **Intercambiar** usa el resultado actual como nueva entrada y **Copiar resultado** usa el portapapeles de Qt.
- Curso: cada una de las seis unidades incluye objetivo, idea clave, sintaxis, ejemplo ejecutable, salida esperada y mini reto.
- Acerca de y README declaran que PySL es un proyecto académico independiente, no oficial del ITLA.
- Privacidad: se retira la matrícula de la aplicación, los datos y el README.
- Se añade `THIRD_PARTY_NOTICES.md`; el ejecutable empaqueta solo la imagen heredada que usa la aplicación.
- Base de datos: recuperación automática ante archivo corrupto y versión de esquema (`user_version`).
- Seguridad: el operador `%` rechaza el formateo de cadenas; la documentación aclara que el límite de memoria solo existe en POSIX.
- Capturas del README regeneradas con `scripts/capture_screenshots.py`.

### Datos y calidad

- SQLite cierra cada conexión (antes `with connection` solo confirmaba la transacción y dejaba el archivo abierto, problemático en Windows).
- Los empates (piedra/papel/tijera, tres en raya) ya no se contabilizan como derrotas.
- Una única instancia de `Database` se comparte entre todas las vistas.
- Los límites de tamaño de fuente se centralizan en `pysl.ui.styles`.
- La suite pasa de 34 a 137 pruebas, incluyendo pruebas de interfaz sin pantalla y la ejecución de cada ejemplo del curso.

## 1.0.4 - 2026-08-08

### Interfaz y experiencia

- Elimina el módulo **Galería** de la navegación y del código fuente; el material histórico permanece preservado en `legacy/web-original/`.
- Implementa temas **Oscuro** y **Claro** funcionales en toda la aplicación.
- Aplica el cambio de tema y tamaño de fuente en tiempo real desde Configuración.
- Restaura automáticamente las preferencias visuales guardadas al iniciar PySL.
- Adapta la numeración de líneas y el resaltado de línea actual del editor al tema activo.
- Mantiene el **Menor número par** como laboratorio, preservando el ejercicio académico original sin duplicarlo como juego.
- Integra el **Ahorcado** original al sistema de estadísticas SQLite compartido por el Arcade PySL.
- Clarifica el convertidor con paneles **Código SL** y **Código Python** según la dirección seleccionada.
- Evita exponer helpers internos del runtime en SL → Python; la salida educativa utiliza `print()` e `input()` estándar.
- Inicializa el ejemplo SL → Python con una conversión visible y mantiene el contenido literal del programa sin modificarlo.

### Calidad

- Añade pruebas automatizadas para normalización de temas y límites del tamaño de fuente.
- Añade pruebas para garantizar que SL → Python no exponga `__imprimir__` ni `__leer__`.
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
