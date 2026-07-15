from __future__ import annotations

from dataclasses import dataclass, field
import random
import unicodedata


WORDS = ("software", "javascript", "videojuego", "programacion", "html", "base de datos", "variable", "fotogramas", "css", "maquina virtual", "nintendo", "algoritmo", "codigo", "pseudocodigo")


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


@dataclass(slots=True)
class HangmanGame:
    word: str
    maximum_failures: int = 6
    used_letters: set[str] = field(default_factory=set)
    failures: int = 0

    @classmethod
    def random(cls, rng: random.Random | None = None) -> "HangmanGame":
        chooser = rng or random
        return cls(chooser.choice(WORDS))

    def guess(self, letter: str) -> bool:
        normalized = normalize(letter.strip())
        if len(normalized) != 1 or not normalized.isalpha():
            raise ValueError("Digite una sola letra válida.")
        if normalized in self.used_letters:
            raise ValueError("Esa letra ya fue utilizada.")
        self.used_letters.add(normalized)
        success = normalized in normalize(self.word)
        if not success:
            self.failures += 1
        return success

    @property
    def masked_word(self) -> str:
        normalized_word = normalize(self.word)
        return " ".join(original if (original == " " or normalized in self.used_letters) else "_" for original, normalized in zip(self.word, normalized_word))

    @property
    def won(self) -> bool:
        return all(char == " " or char in self.used_letters for char in normalize(self.word))

    @property
    def lost(self) -> bool:
        return self.failures >= self.maximum_failures
