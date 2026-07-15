# Sintaxis PySL 1.0

Todo programa contiene `inicio` y `fin`.

```pysl
inicio
cadena nombre
leer(nombre)
imprimir("Hola", nombre)
fin
```

## Tipos

`numerico`, `entero`, `real`, `cadena`, `logico`, `caracter` y `vector`.

## Decisiones

```pysl
si edad >= 18 entonces
    imprimir("Mayor de edad")
sino
    imprimir("Menor de edad")
finsi
```

## Ciclos

```pysl
para i desde 1 hasta 10
    imprimir(i)
finpara
```

```pysl
mientras contador < 5
    contador = contador + 1
finmientras
```

## Vectores

```pysl
vector numeros = [4, 8, 2]
imprimir(numeros[1])
numeros[0] = 10
```

## Funciones

```pysl
funcion sumar(a, b)
    retornar a + b
finfuncion

inicio
resultado = sumar(3, 5)
imprimir(resultado)
fin
```
