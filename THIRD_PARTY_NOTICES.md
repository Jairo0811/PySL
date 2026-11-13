# Avisos de terceros y material heredado

## Alcance de la licencia

La licencia [MIT](LICENSE) cubre el **código original de PySL** (`src/`, `tests/`, `scripts/`, `docs/`, `examples/`) y los recursos creados por el autor para esta plataforma.

PySL es un proyecto académico independiente y **no es un producto oficial del Instituto Tecnológico de Las Américas (ITLA)**. Los nombres, logotipos y marcas mencionados o mostrados pertenecen a sus respectivos propietarios; su presencia no implica afiliación, patrocinio ni respaldo.

## Dependencias

| Componente | Uso | Licencia |
|---|---|---|
| PySide6 / Qt for Python | Interfaz gráfica | LGPLv3 / GPL / comercial (Qt Group) |
| PyInstaller | Empaquetado para Windows (solo desarrollo) | GPLv2 con excepción de distribución |
| Pytest, Ruff | Pruebas y calidad (solo desarrollo) | MIT |

Consulta los términos vigentes de cada proyecto antes de redistribuir binarios.

## Logotipo institucional

`assets/ITLA-logo-fondo-blanco.png` es el logotipo del ITLA, propiedad de la institución. Se muestra únicamente para identificar el contexto académico original (curso y período) en la pantalla *Acerca de*. No forma parte de la licencia MIT.

## Archivo histórico (`legacy/web-original/`)

Es el proyecto web original de 2016, conservado **solo como evidencia histórica**; no se ha eliminado ni modificado. La auditoría del contenido arrojó:

| Categoría | Archivos | Tratamiento |
|---|---|---|
| Código propio (HTML, CSS, JS) | `*.html`, `css/`, `js/` | Autoría del proyecto; cubierto por MIT |
| Foto de perfil del autor | `1.jpg` | Es la única imagen utilizada por la aplicación (página *Mi perfil*) y la única empaquetada en el ejecutable |
| Imágenes y vídeo de terceros (marcas/medios de franquicias de entretenimiento) | `2.jpg`, `3.jpg`, `wwe.PNG`, `11754472_…_o.jpg`, `d82.png`, `Smash4.mp4` | Propiedad de sus titulares; no licenciados bajo MIT; conservados solo como material histórico, no se empaquetan ni se muestran |
| Imágenes de origen incierto (posible material de internet) | `fuego.jpg`, `softwarebg1.jpg`, `42080142-…jpg` | Se desconoce la licencia; igual tratamiento que la fila anterior |
| Fotografías de otras personas (compañeros/conocidos) | `4to.jpg`, `8vo.jpg`, `choconiga.jpg`, `ismael.jpg`, `nahomy.jpg`, `pedb.jpg`, `raideljoan.jpg`, `yunito.jpg`, `13466403_…_n.jpg`, `13820703_…_n.jpg`, `pizap….jpg` | No se usan en la aplicación ni en la documentación. Conservadas únicamente en el archivo histórico; se retirarán a petición de cualquier persona identificable |

### Información personal detectada

- `legacy/web-original/README.md` contiene un identificador estudiantil y las credenciales de demostración del login web de 2016 (validadas en el navegador, sin servidor). Carecen de valor para el portafolio y **no aparecen** en la aplicación, en `data/` ni en la documentación actual. Se mantienen únicamente en el archivo histórico por decisión explícita de no destruir evidencia; su eliminación queda como decisión del autor.
- La versión 1.0.5 no añade datos personales nuevos.

### Si eres titular de derechos o aparecer en una imagen

Abre un *issue* en el repositorio o contacta al mantenedor mediante su perfil de GitHub y el material se retirará.
