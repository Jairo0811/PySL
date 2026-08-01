def cls() -> None:
    """Clear ANSI-compatible terminals, including current Windows consoles."""
    print("\033[2J\033[H", end="")


def pausa(mensaje: str = "Presione Enter para continuar...") -> None:
    input(mensaje)
