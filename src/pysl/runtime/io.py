from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def imprimir(*valores: object, separador: str = " ", fin: str = "\n") -> None:
    """Equivalente PySL de imprimir() en SL."""
    print(*valores, sep=separador, end=fin)


def leer_texto(mensaje: str = "") -> str:
    """Lee texto desde la entrada estándar."""
    return input(mensaje).strip()


def leer_entero(
    mensaje: str = "",
    *,
    input_fn: Callable[[str], str] = input,
    error_fn: Callable[[str], None] = print,
) -> int:
    """Lee un entero y repite la solicitud mientras la entrada sea inválida."""
    while True:
        try:
            return int(input_fn(mensaje).strip())
        except ValueError:
            error_fn("Entrada inválida. Digite un número entero.")
