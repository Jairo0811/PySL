class TicTacToe:
    WIN_LINES = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
    def __init__(self) -> None:
        self.board = [""] * 9
        self.turn = "X"
    def move(self, index: int) -> str | None:
        if index not in range(9) or self.board[index]: raise ValueError("Movimiento inválido")
        self.board[index] = self.turn
        winner = self.winner()
        if not winner: self.turn = "O" if self.turn == "X" else "X"
        return winner
    def winner(self) -> str | None:
        for a,b,c in self.WIN_LINES:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]: return self.board[a]
        return "empate" if all(self.board) else None
