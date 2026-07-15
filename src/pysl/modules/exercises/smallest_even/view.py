from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pysl.modules.exercises.smallest_even.service import SmallestEvenService


SL_CODE = """var
    numeros[5], menorPar, posicion: numerico
    i: numerico

inicio
    para (i = 0; i < 5; i = i + 1)
        leer(numeros[i])
    finpara

    menorPar = 999999
    posicion = -1

    para (i = 0; i < 5; i = i + 1)
        si (numeros[i] % 2 == 0 y numeros[i] < menorPar)
            menorPar = numeros[i]
            posicion = i
        finsi
    finpara

    imprimir(menorPar, posicion)
fin"""

PYTHON_CODE = """def buscar_menor_par(numeros: list[int]) -> tuple[int, int] | None:
    pares = [(indice, numero) for indice, numero in enumerate(numeros)
             if numero % 2 == 0]

    if not pares:
        return None

    indice, menor = min(pares, key=lambda elemento: elemento[1])
    return menor, indice"""


class SmallestEvenView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._service = SmallestEvenService()
        self._inputs: list[QLineEdit] = []
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(16)

        title = QLabel("Menor número par")
        title.setObjectName("title")
        subtitle = QLabel(
            "Digite cinco números. PySL encontrará el menor número par y resaltará su posición."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        input_group = QGroupBox("Datos de entrada")
        input_layout = QGridLayout(input_group)
        for index in range(self._service.REQUIRED_VALUES):
            label = QLabel(f"Número {index + 1}")
            field = QLineEdit()
            field.setPlaceholderText("0")
            field.setAlignment(Qt.AlignmentFlag.AlignCenter)
            field.returnPressed.connect(self._solve)
            self._inputs.append(field)
            input_layout.addWidget(label, 0, index)
            input_layout.addWidget(field, 1, index)

        actions = QHBoxLayout()
        solve_button = QPushButton("Resolver ejercicio")
        solve_button.clicked.connect(self._solve)
        clear_button = QPushButton("Limpiar")
        clear_button.setObjectName("secondaryButton")
        clear_button.clicked.connect(self._clear)
        actions.addWidget(solve_button)
        actions.addWidget(clear_button)
        actions.addStretch()

        self._result_label = QLabel("Esperando datos...")
        self._result_label.setObjectName("resultLabel")

        self._table = QTableWidget(1, self._service.REQUIRED_VALUES)
        self._table.setHorizontalHeaderLabels([f"Posición {i}" for i in range(5)])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setMaximumHeight(115)
        self._table.horizontalHeader().setStretchLastSection(True)

        code_tabs = QTabWidget()
        code_tabs.addTab(self._code_view(SL_CODE), "Algoritmo SL")
        code_tabs.addTab(self._code_view(PYTHON_CODE), "Implementación Python")

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(input_group)
        root.addLayout(actions)
        root.addWidget(self._result_label)
        root.addWidget(self._table)
        root.addWidget(code_tabs, 1)

    @staticmethod
    def _code_view(code: str) -> QTextEdit:
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(code)
        editor.setObjectName("codeEditor")
        return editor

    def _solve(self) -> None:
        try:
            values = [int(field.text().strip()) for field in self._inputs]
        except ValueError:
            QMessageBox.warning(self, "Datos inválidos", "Todos los campos deben contener enteros.")
            return

        result = self._service.solve(values)
        self._render_result(result.values, result.index)

        if result.found:
            self._result_label.setText(
                f"Resultado: {result.smallest_even} es el menor par y está en la posición {result.index}."
            )
        else:
            self._result_label.setText("Resultado: no se encontró ningún número par.")

    def _render_result(self, values: tuple[int, ...], highlighted_index: int | None) -> None:
        for index, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if index == highlighted_index:
                item.setBackground(Qt.GlobalColor.blue)
            else:
                item.setBackground(Qt.GlobalColor.red)
            item.setForeground(Qt.GlobalColor.white)
            self._table.setItem(0, index, item)

    def _clear(self) -> None:
        for field in self._inputs:
            field.clear()
        self._table.clearContents()
        self._result_label.setText("Esperando datos...")
        self._inputs[0].setFocus()
