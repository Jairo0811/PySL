from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QSplitter, QVBoxLayout, QWidget

from pysl.modules.course.lessons import LESSONS


class CourseView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._lessons = {lesson.title: lesson for lesson in LESSONS}
        root = QVBoxLayout(self)
        title = QLabel("Curso de Fundamentos")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Ruta compacta para aprender programación estructurada con SL. "
            "Copia cada ejemplo en el IDE para ejecutarlo."
        )
        subtitle.setObjectName("subtitle")
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list = QListWidget()
        self.list.addItems(list(self._lessons))
        self.content = QPlainTextEdit()
        self.content.setObjectName("codeEditor")
        self.content.setReadOnly(True)
        self.list.currentTextChanged.connect(self._show_lesson)
        splitter.addWidget(self.list)
        splitter.addWidget(self.content)
        splitter.setStretchFactor(1, 1)
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(splitter, 1)
        self.list.setCurrentRow(0)

    def _show_lesson(self, title: str) -> None:
        lesson = self._lessons.get(title)
        self.content.setPlainText(lesson.render() if lesson else "")
