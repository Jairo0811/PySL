import pytest

from pysl.modules.exercises.smallest_even.service import SmallestEvenService


def test_finds_smallest_even_and_its_zero_based_index() -> None:
    result = SmallestEvenService().solve([9, 4, 7, 2, 6])

    assert result.smallest_even == 2
    assert result.index == 3
    assert result.found is True


def test_reports_when_there_are_no_even_numbers() -> None:
    result = SmallestEvenService().solve([9, 3, 7, 5, 1])

    assert result.smallest_even is None
    assert result.index is None
    assert result.found is False


def test_requires_exactly_five_numbers() -> None:
    with pytest.raises(ValueError, match="exactamente 5"):
        SmallestEvenService().solve([2, 4])
