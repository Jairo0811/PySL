from pysl.modules.games.guess_number.service import GuessNumberGame
from pysl.modules.games.rock_paper_scissors.service import play
from pysl.modules.games.tic_tac_toe.service import TicTacToe

def test_guess_number() -> None:
    game = GuessNumberGame(50)
    assert game.guess(30) == "mayor"
    assert game.guess(70) == "menor"
    assert game.guess(50) == "correcto"

def test_rps() -> None:
    assert play("piedra", "tijera")[0] == "ganaste"

def test_tic_tac_toe() -> None:
    game = TicTacToe()
    for move in (0,3,1,4): game.move(move)
    assert game.move(2) == "X"
