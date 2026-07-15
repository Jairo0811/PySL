import os


def cls() -> None:
    """Limpia la consola en Windows, Linux y macOS."""
    os.system("cls" if os.name == "nt" else "clear")


def pausa(mensaje: str = "Presione Enter para continuar...") -> None:
    input(mensaje)
