import random

CHOICES = ("piedra", "papel", "tijera")

def play(user: str, computer: str | None = None) -> tuple[str, str]:
    user = user.lower()
    if user not in CHOICES: raise ValueError("Jugada inválida")
    computer = computer or random.choice(CHOICES)
    if user == computer: result = "empate"
    elif (user, computer) in {("piedra","tijera"),("papel","piedra"),("tijera","papel")}: result = "ganaste"
    else: result = "perdiste"
    return result, computer
