from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class SmallestEvenResult:
    values: tuple[int, ...]
    smallest_even: int | None
    index: int | None

    @property
    def found(self) -> bool:
        return self.smallest_even is not None and self.index is not None


class SmallestEvenService:
    REQUIRED_VALUES = 5

    def solve(self, values: Sequence[int]) -> SmallestEvenResult:
        if len(values) != self.REQUIRED_VALUES:
            raise ValueError(f"Se requieren exactamente {self.REQUIRED_VALUES} números.")

        normalized = tuple(int(value) for value in values)
        even_candidates = [
            (index, value)
            for index, value in enumerate(normalized)
            if value % 2 == 0
        ]

        if not even_candidates:
            return SmallestEvenResult(normalized, None, None)

        index, value = min(even_candidates, key=lambda candidate: candidate[1])
        return SmallestEvenResult(normalized, value, index)
