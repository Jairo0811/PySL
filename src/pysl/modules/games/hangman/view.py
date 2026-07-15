from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pysl.modules.games.hangman.service import HangmanGame

STAGES = (
    "",
    "O",
    "O\n|",
    " O\n/|",
    " O\n/|\\",
    " O\n/|\\\n/",
    " O\n/|\\\n/ \\",
)


class HangmanView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._game = HangmanGame.random()
        self._wins = 0
        self._losses = 0
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        title = QLabel("Ahorcado PySL")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Versión moderna del juego incluido en el proyecto final original.")
        subtitle.setObjectName("subtitle")
        self._stage = QLabel()
        self._stage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stage.setStyleSheet("font-family: Consolas; font-size: 36px; min-height: 180px;")
        self._word = QLabel()
        self._word.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._word.setStyleSheet("font-family: Consolas; font-size: 28px; font-weight: 700;")
        self._status = QLabel()
        self._status.setObjectName("resultLabel")
        row = QHBoxLayout()
        self._letter = QLineEdit()
        self._letter.setMaxLength(1)
        self._letter.setPlaceholderText("Letra")
        self._letter.returnPressed.connect(self._guess)
        guess = QPushButton("Comprobar")
        guess.clicked.connect(self._guess)
        new = QPushButton("Nueva partida")
        new.setObjectName("secondaryButton")
        new.clicked.connect(self._new_game)
        row.addWidget(self._letter)
        row.addWidget(guess)
        row.addWidget(new)
        row.addStretch()
        self._used = QLabel()
        self._used.setObjectName("subtitle")
        self._score = QLabel()
        self._score.setObjectName("accent")
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(self._stage)
        root.addWidget(self._word)
        root.addLayout(row)
        root.addWidget(self._used)
        root.addWidget(self._status)
        root.addWidget(self._score)
        root.addStretch()

    def _guess(self) -> None:
        try:
            self._game.guess(self._letter.text())
            self._letter.clear()
            self._refresh()
            if self._game.won:
                self._wins += 1
                QMessageBox.information(
                    self,
                    "¡Victoria!",
                    f"¡Compai, tú eres un duro! La palabra era: {self._game.word}",
                )
                self._new_game()
            elif self._game.lost:
                self._losses += 1
                QMessageBox.warning(
                    self,
                    "Partida terminada",
                    f"La macate, loco. La palabra era: {self._game.word}",
                )
                self._new_game()
        except ValueError as exc:
            QMessageBox.warning(self, "Entrada inválida", str(exc))

    def _new_game(self) -> None:
        self._game = HangmanGame.random()
        self._letter.clear()
        self._refresh()
        self._letter.setFocus()

    def _refresh(self) -> None:
        self._stage.setText(STAGES[min(self._game.failures, 6)])
        self._word.setText(self._game.masked_word)
        self._used.setText("Letras usadas: " + ", ".join(sorted(self._game.used_letters)))
        self._status.setText(f"Fallos: {self._game.failures}/{self._game.maximum_failures}")
        self._score.setText(f"Victorias: {self._wins}  •  Derrotas: {self._losses}")
