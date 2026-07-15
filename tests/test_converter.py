from pysl.modules.converter.service import CodeConverter


def test_converts_pysl_to_python() -> None:
    converted = CodeConverter().pysl_to_python('inicio\nimprimir("Hola")\nfin')
    assert '__imprimir__("Hola")' in converted


def test_converts_basic_python_to_pysl() -> None:
    converted = CodeConverter().python_to_pysl(
        'nombre = input("Nombre: ")\nprint(nombre)'
    )
    assert "leer(nombre)" in converted
    assert "imprimir(nombre)" in converted
