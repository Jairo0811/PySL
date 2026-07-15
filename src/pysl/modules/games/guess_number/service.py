import random

class GuessNumberGame:
    def __init__(self, target: int | None = None) -> None:
        self.target = target if target is not None else random.randint(1, 100)
        self.attempts = 0
    def guess(self, value: int) -> str:
        self.attempts += 1
        if value == self.target: return "correcto"
        return "mayor" if value < self.target else "menor"
