import pytest
from pysl.modules.games.hangman.service import HangmanGame


def test_correct_and_incorrect_guesses() -> None:
    game = HangmanGame("codigo")
    assert game.guess("c") is True
    assert game.guess("x") is False
    assert game.failures == 1
    assert "c" in game.masked_word


def test_repeated_letter_is_rejected() -> None:
    game = HangmanGame("python")
    game.guess("p")
    with pytest.raises(ValueError):
        game.guess("p")
