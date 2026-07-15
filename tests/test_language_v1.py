from pysl.language.executor import PySLExecutor

def test_vectors_and_functions() -> None:
    source = '''
funcion sumar(a, b)
    retornar a + b
finfuncion
inicio
vector numeros = [2, 4, 6]
numeros[0] = sumar(numeros[1], numeros[2])
imprimir(numeros[0])
fin
'''
    result = PySLExecutor().execute(source)
    assert result.output == "10"
    assert result.variables["numeros"] == [10, 4, 6]

def test_nested_blocks() -> None:
    source = '''
inicio
entero total = 0
para i desde 1 hasta 3
    si i > 1 entonces
        total = total + i
    finsi
finpara
imprimir(total)
fin
'''
    assert PySLExecutor().execute(source).output == "5"
