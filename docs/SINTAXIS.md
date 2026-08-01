# Sintaxis de SL 1.0

SL (Structured Language) es el lenguaje educativo soportado por la plataforma PySL. Todo programa ejecutable contiene exactamente un bloque `inicio` / `fin`. Las funciones pueden declararse antes del bloque principal.

## Programa mínimo

```text
inicio
imprimir("Hola")
fin
```

Los comentarios comienzan con `//` o `#` y ocupan el resto de la línea.

## Tipos y variables

Las declaraciones educativas admitidas son `numerico`, `entero`, `real`, `cadena`, `logico`, `caracter` y `vector`.

```text
inicio
entero edad = 28
cadena nombre = "Jairo"
logico activo = verdadero
vector notas = [90, 85, 100]
fin
```

Una declaración sin valor se inicializa como `None` en la representación interna.

## Entrada y salida

```text
inicio
leer(nombre)
imprimir("Hola", nombre)
fin
```

`leer` convierte automáticamente entradas que representan enteros, reales o valores lógicos. Las entradas restantes se conservan como texto.

## Operadores

| Grupo | Operadores |
|---|---|
| Aritméticos | `+`, `-`, `*`, `/`, `//`, `%`, `**` |
| Comparación | `==`, `<>`, `<`, `<=`, `>`, `>=` |
| Lógicos | `y`, `o`, `no` |
| Lógicos literales | `verdadero`, `falso` |

Las palabras lógicas dentro de cadenas no se modifican.

## Decisiones

```text
si edad >= 18 entonces
    imprimir("Mayor de edad")
sino
    imprimir("Menor de edad")
finsi
```

`sino` es opcional. Cada rama debe contener al menos una instrucción.

## Ciclos

`hasta` es inclusivo:

```text
para i desde 1 hasta 10
    imprimir(i)
finpara
```

```text
mientras contador < 5
    contador = contador + 1
finmientras
```

## Vectores

Los índices comienzan en cero:

```text
inicio
vector numeros = [4, 8, 2]
imprimir(numeros[1])
numeros[0] = 10
fin
```

## Funciones

```text
funcion sumar(a, b)
    retornar a + b
finfuncion

inicio
resultado = sumar(3, 5)
imprimir(resultado)
fin
```

Los parámetros son posicionales, no pueden repetirse y no admiten valores predeterminados en SL 1.0.

## Funciones autorizadas

Además de funciones declaradas por el estudiante, el runtime admite `int`, `float`, `str`, `range`, `len`, `min`, `max` y `sum`. No se permiten imports, atributos, decoradores, comprensiones ni acceso al sistema.

## Límites predeterminados

| Recurso | Límite |
|---|---:|
| Tiempo | 3 segundos |
| Pasos | 100,000 |
| Iteraciones por `para` | 10,000 |
| Salida | 10,000 líneas / 100,000 caracteres |
| AST | 5,000 nodos |
| Colecciones | 10,000 elementos |

Estos valores protegen la aplicación y pueden ajustarse mediante `ExecutionLimits` en integraciones controladas.
