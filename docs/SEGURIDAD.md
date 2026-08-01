# Seguridad

## Modelo de confianza

El runtime permite ejecutar ejercicios SL escritos por el usuario local. Reduce el riesgo de errores accidentales y programas que no terminan, pero no pretende sustituir una sandbox de sistema operativo para código hostil de terceros.

## Controles aplicados

1. El parser acepta únicamente instrucciones de SL 1.0.
2. Cada expresión debe ser una expresión sintáctica completa; no se admiten inyecciones mediante `;`.
3. El AST generado utiliza una lista explícita de nodos permitidos.
4. Las llamadas se limitan a entrada/salida, funciones declaradas y utilidades numéricas autorizadas.
5. Los nombres internos y los identificadores que comienzan con `_` están reservados.
6. El programa se ejecuta en otro proceso sin `__builtins__` generales.
7. Se aplican límites de tiempo, pasos, ciclos, AST, entrada, salida, colecciones y enteros.
8. En sistemas POSIX se aplica además `RLIMIT_AS`; en Windows se mantienen el aislamiento de proceso y los límites lógicos.
9. La interfaz ejecuta el servicio en un worker de Qt y permanece receptiva.

## Datos locales

- SQLite usa consultas parametrizadas.
- La base y los logs se almacenan en la carpeta de datos del usuario.
- El login es demostrativo y local; ofrece acceso explícito como invitado y la cuenta académica compatible compara su contraseña con un derivado PBKDF2.
- Los logs rotan y no registran contraseñas ni el contenido de las entradas del programa.

## Reporte de vulnerabilidades

No publiques información sensible en un issue. Utiliza la opción **Report a vulnerability** del repositorio si está disponible o contacta al mantenedor mediante su perfil de GitHub.

Consulta también [SECURITY.md](../SECURITY.md).
