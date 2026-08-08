# 🕰️ PySL — Proyecto web original (2016)

> **Archivo histórico del proyecto final de Fundamentos de Programación (SOF-001).**

Este directorio conserva la versión web original desarrollada durante el período académico **2016-C2** en el **Instituto Tecnológico de Las Américas (ITLA)**.

Forma parte de la historia de **PySL** y permite comparar directamente el proyecto académico de 2016 con su restauración y evolución profesional realizada en 2026.

## 🎓 Información académica

- **Institución:** Instituto Tecnológico de Las Américas (ITLA)
- **Materia:** Fundamentos de Programación (SOF-001)
- **Autor:** Francis Jairo Matías Rosario
- **Matrícula:** 2015-2984
- **Período académico:** 2016-C2
- **Profesor:** Freidy Ramón Núñez Pérez

## 🧰 Tecnologías originales

<p>
  <img src="https://skillicons.dev/icons?i=html,css,js" alt="HTML, CSS y JavaScript" />
</p>

El proyecto fue construido como una aplicación web estática utilizando **HTML, CSS y JavaScript**, sin frameworks ni backend.

## 📚 ¿Qué contiene?

La versión histórica incluye:

- Inicio de sesión demostrativo.
- Página principal y navegación.
- Perfil del estudiante.
- Galería de imágenes.
- Juego del Ahorcado.
- Ejercicio del menor número par.
- Recursos gráficos y audiovisuales originales.

## ▶️ Cómo ejecutarlo

No requiere instalación de dependencias ni compilación.

Puedes abrir directamente:

```text
iniciarsecion.html
```

en un navegador web.

Para una ejecución más consistente también puedes servir esta carpeta con el servidor HTTP integrado de Python:

```powershell
cd legacy/web-original
python -m http.server 8000
```

Después abre en el navegador:

```text
http://localhost:8000/iniciarsecion.html
```

## 🔐 Acceso histórico

El inicio de sesión pertenece exclusivamente a la demostración académica original y funciona del lado del cliente.

```text
Usuario: Jairo
Contraseña: jairomatias
```

> ⚠️ **Importante:** este mecanismo no constituye autenticación segura y no debe utilizarse como referencia para aplicaciones de producción. Se conserva únicamente por razones históricas y demostrativas.

## 🛠️ Restauración técnica

En 2026 se realizó una restauración conservadora del código de esta versión para facilitar su ejecución en navegadores actuales sin alterar deliberadamente su identidad visual.

Entre los ajustes realizados se encuentran:

- Estructura HTML5 válida.
- Codificación UTF-8.
- Separación de HTML, CSS y JavaScript.
- Eliminación de APIs JavaScript obsoletas.
- Sustitución de eventos inline por `addEventListener`.
- Eliminación de `document.write()` en el ejercicio algorítmico.
- Corrección de errores del Ahorcado y selección aleatoria de palabras.
- Uso de elementos HTML modernos para contenido multimedia.
- Limpieza de etiquetas inválidas y código duplicado.

La intención de esta restauración **no es rediseñar el proyecto de 2016**, sino mantenerlo funcional y reconocible para documentar de dónde nació PySL.

## 🧭 2016 → 2026

```text
2016                                      2026
  │                                         │
  ├─ Proyecto académico                     ├─ Plataforma educativa de escritorio
  ├─ HTML / CSS / JavaScript                ├─ Python / PySide6
  ├─ Ejercicios básicos                     ├─ Lenguaje educativo SL
  ├─ Ahorcado                               ├─ IDE de SL
  └─ Fundamentos de programación            ├─ SL ↔ Python
                                            ├─ Runtime seguro
                                            ├─ Curso y laboratorios
                                            ├─ Juegos educativos
                                            ├─ SQLite
                                            └─ Pruebas automatizadas
```

La aplicación moderna no pretende borrar este proyecto. **PySL 2026 existe precisamente porque este proyecto existió primero.**

## 📁 Proyecto moderno

Para conocer la versión actual, arquitectura, instalación, lenguaje SL y demás documentación, vuelve al [`README.md`](../../README.md) principal del repositorio.

---

<p align="center">
  <strong>Del proyecto académico al software profesional.</strong><br>
  PySL · 2016 → 2026
</p>
