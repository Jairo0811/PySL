from PySide6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget
from pysl.core.database import Database
from pysl.modules.games.hangman.view import HangmanView
from pysl.modules.games.guess_number.service import GuessNumberGame
from pysl.modules.games.rock_paper_scissors.service import play
from pysl.modules.games.tic_tac_toe.service import TicTacToe

class GuessView(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__(); self.db=db; self.game=GuessNumberGame(); layout=QVBoxLayout(self)
        layout.addWidget(QLabel("Adivina un número entre 1 y 100")); self.value=QSpinBox(); self.value.setRange(1,100); layout.addWidget(self.value)
        self.result=QLabel(); button=QPushButton("Probar"); button.clicked.connect(self.guess); layout.addWidget(button); layout.addWidget(self.result); layout.addStretch()
    def guess(self):
        result=self.game.guess(self.value.value()); self.result.setText({"mayor":"El número secreto es mayor.","menor":"El número secreto es menor.","correcto":f"¡Correcto en {self.game.attempts} intentos!"}[result])
        if result=="correcto": self.db.record_game("guess", True); self.game=GuessNumberGame()
class RpsView(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__(); self.db=db; layout=QVBoxLayout(self); self.choice=QComboBox(); self.choice.addItems(["piedra","papel","tijera"]); self.result=QLabel(); button=QPushButton("Jugar"); button.clicked.connect(self.run); layout.addWidget(self.choice); layout.addWidget(button); layout.addWidget(self.result); layout.addStretch()
    def run(self):
        result, computer=play(self.choice.currentText()); self.result.setText(f"Computadora: {computer}. Resultado: {result}."); self.db.record_game("rps", result=="ganaste")
class TicView(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__(); self.db=db; self.game=TicTacToe(); self.buttons=[]; root=QVBoxLayout(self); self.status=QLabel("Turno: X"); grid=QGridLayout()
        for i in range(9):
            b=QPushButton(" "); b.setMinimumSize(90,70); b.clicked.connect(lambda _, x=i:self.move(x)); self.buttons.append(b); grid.addWidget(b,i//3,i%3)
        reset=QPushButton("Reiniciar"); reset.clicked.connect(self.reset); root.addWidget(self.status); root.addLayout(grid); root.addWidget(reset); root.addStretch()
    def move(self,index):
        try: winner=self.game.move(index); self.buttons[index].setText(self.game.board[index])
        except ValueError: return
        if winner:
            self.status.setText(f"Resultado: {winner}"); self.db.record_game("tic_tac_toe", winner in {"X","O"})
            for b in self.buttons: b.setEnabled(False)
        else: self.status.setText(f"Turno: {self.game.turn}")
    def reset(self):
        self.game=TicTacToe(); self.status.setText("Turno: X")
        for b in self.buttons: b.setText(" "); b.setEnabled(True)
class GamesView(QWidget):
    def __init__(self) -> None:
        super().__init__(); db=Database(); root=QVBoxLayout(self); title=QLabel("Arcade PySL"); title.setObjectName("pageTitle"); tabs=QTabWidget(); tabs.addTab(HangmanView(),"Ahorcado"); tabs.addTab(GuessView(db),"Adivina el número"); tabs.addTab(RpsView(db),"Piedra, papel o tijera"); tabs.addTab(TicView(db),"Tres en raya"); root.addWidget(title); root.addWidget(tabs,1)
