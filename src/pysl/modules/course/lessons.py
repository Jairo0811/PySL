"""Contenido del curso integrado. Cada ejemplo es un programa SL 1.0 ejecutable."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Lesson:
    title: str
    explanation: str
    example: str
    inputs: tuple[str, ...] = ()
    expected_output: str = ""

    def render(self) -> str:
        parts = [self.explanation, "Ejemplo:", self.example]
        if self.expected_output:
            parts.extend(["Salida esperada:", self.expected_output])
        return "\n\n".join(parts)


LESSONS: tuple[Lesson, ...] = (
    Lesson(
        title="1. Variables y tipos",
        explanation=(
            "Una variable guarda un valor con un nombre. SL ofrece las declaraciones "
            "numerico, entero, real, cadena, logico, caracter y vector; declarar es opcional, "
            "pero ayuda a documentar la intención del programa.\n\n"
            "Los nombres no pueden coincidir con palabras reservadas de Python como class, "
            "import o lambda."
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
    ),
    Lesson(
        title="2. Condicionales",
        explanation=(
            "Usa si, sino y finsi para tomar decisiones. Combina condiciones con y, o, no y "
            "compáralas con ==, <>, <, <=, > y >=. Cada rama debe tener al menos una "
            "instrucción."
        ),
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
    ),
    Lesson(
        title="3. Ciclos",
        explanation=(
            "Repite instrucciones con para (cantidad conocida de repeticiones) o mientras "
            "(mientras una condición sea verdadera). En para, el límite hasta es inclusivo."
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
    ),
    Lesson(
        title="4. Vectores",
        explanation=(
            "Un vector agrupa varios valores bajo un mismo nombre. Los índices comienzan en "
            "cero y len(vector) devuelve la cantidad de elementos. Acceder a un índice que no "
            "existe produce un error que indica la línea exacta."
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
    ),
    Lesson(
        title="5. Funciones",
        explanation=(
            "Divide un algoritmo en partes reutilizables con funcion, retornar y finfuncion. "
            "Las funciones se declaran antes del bloque inicio y pueden llamarse a sí mismas "
            "(recursión), siempre que exista un caso base."
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
    ),
    Lesson(
        title="6. Proyecto final",
        explanation=(
            "Combina entrada, decisiones, ciclos, vectores y funciones. Este programa lee un "
            "límite y reúne los números pares hasta ese valor. En el IDE escribe el límite en "
            "el campo de entradas (por ejemplo, 6)."
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
    ),
)
