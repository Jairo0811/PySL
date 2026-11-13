"""Contenido del curso integrado. Cada ejemplo y cada solución de reto es SL 1.0 ejecutable."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Lesson:
    title: str
    objective: str
    explanation: str
    syntax: str
    example: str
    challenge: str
    challenge_solution: str
    inputs: tuple[str, ...] = ()
    expected_output: str = ""
    challenge_inputs: tuple[str, ...] = ()
    challenge_output: str = ""

    def render(self) -> str:
        parts = [
            f"OBJETIVO\n{self.objective}",
            f"IDEA CLAVE\n{self.explanation}",
            f"SINTAXIS\n{self.syntax}",
            f"EJEMPLO\n{self.example}",
        ]
        if self.expected_output:
            parts.append(f"SALIDA ESPERADA\n{self.expected_output}")
        parts.append(f"MINI RETO\n{self.challenge}")
        return "\n\n".join(parts)


LESSONS: tuple[Lesson, ...] = (
    Lesson(
        title="1. Variables y tipos",
        objective="Guardar datos con nombre y mostrarlos en pantalla.",
        explanation=(
            "Una variable es un nombre que guarda un valor. Declarar el tipo es opcional, pero "
            "documenta qué piensas guardar. Los nombres no pueden ser palabras reservadas de "
            "Python como class, import o lambda."
        ),
        syntax=(
            "entero edad = 28          // también: numerico, real\n"
            'cadena nombre = "Ana"     // también: caracter\n'
            "logico activo = verdadero // o falso\n"
            "imprimir(nombre, edad)"
        ),
        example=(
            "inicio\n"
            "    entero edad = 28\n"
            '    cadena nombre = "Ana"\n'
            "    logico activo = verdadero\n"
            "    imprimir(nombre, edad, activo)\n"
            "fin"
        ),
        expected_output="Ana 28 True",
        challenge=(
            "Guarda tu nombre y tu año de nacimiento en variables y calcula tu edad aproximada "
            "con la resta (2026 - nacimiento). Imprime ambos datos."
        ),
        challenge_solution=(
            "inicio\n"
            '    cadena nombre = "Ana"\n'
            "    entero nacimiento = 2000\n"
            "    entero edad = 2026 - nacimiento\n"
            "    imprimir(nombre, edad)\n"
            "fin"
        ),
        challenge_output="Ana 26",
    ),
    Lesson(
        title="2. Condicionales",
        objective="Hacer que el programa elija un camino según una condición.",
        explanation=(
            "si evalúa una condición; si es verdadera ejecuta su bloque y, si no, ejecuta sino. "
            "Combina condiciones con y, o, no y compara con ==, <>, <, <=, > y >=. Cada rama "
            "debe tener al menos una instrucción."
        ),
        syntax=("si condicion entonces\n    // instrucciones\nsino\n    // instrucciones\nfinsi"),
        example=(
            "inicio\n"
            "    entero edad = 20\n"
            "    si edad >= 18 entonces\n"
            '        imprimir("Mayor de edad")\n'
            "    sino\n"
            '        imprimir("Menor de edad")\n'
            "    finsi\n"
            "fin"
        ),
        expected_output="Mayor de edad",
        challenge=(
            "Lee un número y di si es positivo, negativo o cero. Pista: necesitas un si dentro "
            "del sino. Pruébalo en el IDE escribiendo 5, -3 y 0 en el campo de entradas."
        ),
        challenge_solution=(
            "inicio\n"
            "    leer(n)\n"
            "    si n > 0 entonces\n"
            '        imprimir("positivo")\n'
            "    sino\n"
            "        si n < 0 entonces\n"
            '            imprimir("negativo")\n'
            "        sino\n"
            '            imprimir("cero")\n'
            "        finsi\n"
            "    finsi\n"
            "fin"
        ),
        challenge_inputs=("-3",),
        challenge_output="negativo",
    ),
    Lesson(
        title="3. Ciclos",
        objective="Repetir instrucciones sin copiarlas varias veces.",
        explanation=(
            "Usa para cuando sabes cuántas veces repetir (el límite hasta es inclusivo) y "
            "mientras cuando repites hasta que una condición deje de cumplirse. En mientras, "
            "recuerda modificar la variable de la condición para que el ciclo termine."
        ),
        syntax=(
            "para i desde 1 hasta 5\n"
            "    // se repite con i = 1, 2, 3, 4, 5\n"
            "finpara\n"
            "\n"
            "mientras condicion\n"
            "    // se repite mientras sea verdadera\n"
            "finmientras"
        ),
        example=(
            "inicio\n"
            "    entero suma = 0\n"
            "    para i desde 1 hasta 5\n"
            "        suma = suma + i\n"
            "    finpara\n"
            "    mientras suma > 10\n"
            "        suma = suma - 5\n"
            "    finmientras\n"
            "    imprimir(suma)\n"
            "fin"
        ),
        expected_output="10",
        challenge="Imprime la tabla de multiplicar de un número leído, del 1 al 10 (3 x 1 = 3 ...).",
        challenge_solution=(
            "inicio\n"
            "    leer(n)\n"
            "    para i desde 1 hasta 10\n"
            '        imprimir(n, "x", i, "=", n * i)\n'
            "    finpara\n"
            "fin"
        ),
        challenge_inputs=("3",),
        challenge_output=(
            "3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n3 x 4 = 12\n3 x 5 = 15\n"
            "3 x 6 = 18\n3 x 7 = 21\n3 x 8 = 24\n3 x 9 = 27\n3 x 10 = 30"
        ),
    ),
    Lesson(
        title="4. Vectores",
        objective="Guardar varios valores bajo un solo nombre y recorrerlos.",
        explanation=(
            "Un vector agrupa valores y se accede a ellos por posición. Los índices comienzan "
            "en cero y len(vector) devuelve la cantidad de elementos. Usar un índice que no "
            "existe produce un error que indica la línea exacta."
        ),
        syntax=(
            "vector notas = [90, 85, 100]\n"
            "notas[1] = 95         // cambia el segundo elemento\n"
            "imprimir(notas[0], len(notas))"
        ),
        example=(
            "inicio\n"
            "    vector notas = [90, 85, 100]\n"
            "    notas[1] = 95\n"
            "    total = 0\n"
            "    para i desde 0 hasta len(notas) - 1\n"
            "        total = total + notas[i]\n"
            "    finpara\n"
            '    imprimir("Promedio:", total / len(notas))\n'
            "fin"
        ),
        expected_output="Promedio: 95.0",
        challenge="Encuentra la nota mayor de [72, 95, 88, 60] recorriendo el vector con un ciclo.",
        challenge_solution=(
            "inicio\n"
            "    vector notas = [72, 95, 88, 60]\n"
            "    mayor = notas[0]\n"
            "    para i desde 1 hasta len(notas) - 1\n"
            "        si notas[i] > mayor entonces\n"
            "            mayor = notas[i]\n"
            "        finsi\n"
            "    finpara\n"
            "    imprimir(mayor)\n"
            "fin"
        ),
        challenge_output="95",
    ),
    Lesson(
        title="5. Funciones",
        objective="Dividir un algoritmo en partes con nombre que puedas reutilizar.",
        explanation=(
            "Una función recibe parámetros y devuelve un valor con retornar. Se declara antes "
            "del bloque inicio y puede llamarse a sí misma (recursión), siempre que tenga un "
            "caso base que la detenga."
        ),
        syntax=(
            "funcion nombre(parametro1, parametro2)\n"
            "    retornar parametro1 + parametro2\n"
            "finfuncion"
        ),
        example=(
            "funcion factorial(n)\n"
            "    si n <= 1 entonces\n"
            "        retornar 1\n"
            "    finsi\n"
            "    retornar n * factorial(n - 1)\n"
            "finfuncion\n"
            "\n"
            "inicio\n"
            "    imprimir(factorial(5))\n"
            "fin"
        ),
        expected_output="120",
        challenge="Escribe una función cuadrado(n) y úsala para imprimir el cuadrado de 7.",
        challenge_solution=(
            "funcion cuadrado(n)\n"
            "    retornar n * n\n"
            "finfuncion\n"
            "\n"
            "inicio\n"
            "    imprimir(cuadrado(7))\n"
            "fin"
        ),
        challenge_output="49",
    ),
    Lesson(
        title="6. Proyecto final",
        objective="Combinar entrada, decisiones, ciclos, vectores y funciones en un programa.",
        explanation=(
            "Este programa lee un límite y reúne los números pares hasta ese valor. En el IDE "
            "escribe el límite en el campo de entradas (por ejemplo, 6). Observa cómo cada "
            "tema anterior aporta una pieza."
        ),
        syntax=(
            "funcion ...        // lógica reutilizable\n"
            "inicio\n"
            "    leer(dato)     // entrada\n"
            "    para / mientras / si ...\n"
            "    imprimir(...)  // salida\n"
            "fin"
        ),
        example=(
            "funcion es_par(numero)\n"
            "    retornar numero % 2 == 0\n"
            "finfuncion\n"
            "\n"
            "inicio\n"
            "    leer(limite)\n"
            "    vector pares = []\n"
            "    para i desde 1 hasta limite\n"
            "        si es_par(i) entonces\n"
            "            pares = pares + [i]\n"
            "        finsi\n"
            "    finpara\n"
            '    imprimir("Pares:", pares)\n'
            "fin"
        ),
        inputs=("6",),
        expected_output="Pares: [2, 4, 6]",
        challenge=(
            "Modifica el programa para que además imprima cuántos pares encontró (usa len(pares))."
        ),
        challenge_solution=(
            "funcion es_par(numero)\n"
            "    retornar numero % 2 == 0\n"
            "finfuncion\n"
            "\n"
            "inicio\n"
            "    leer(limite)\n"
            "    vector pares = []\n"
            "    para i desde 1 hasta limite\n"
            "        si es_par(i) entonces\n"
            "            pares = pares + [i]\n"
            "        finsi\n"
            "    finpara\n"
            '    imprimir("Pares:", pares)\n'
            '    imprimir("Cantidad:", len(pares))\n'
            "fin"
        ),
        challenge_inputs=("6",),
        challenge_output="Pares: [2, 4, 6]\nCantidad: 3",
    ),
)
