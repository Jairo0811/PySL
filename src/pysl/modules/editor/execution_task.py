from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from pysl.language.executor import ExecutionResult, SLExecutor


class ExecutionSignals(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    completed = Signal()


class ExecutionTask(QRunnable):
    """Run the isolated SL executor outside Qt's interface thread."""

    def __init__(self, source: str, inputs: list[str]) -> None:
        super().__init__()
        self._source = source
        self._inputs = inputs
        self.signals = ExecutionSignals()

    @Slot()
    def run(self) -> None:
        try:
            result: ExecutionResult = SLExecutor().execute(self._source, self._inputs)
            self.signals.succeeded.emit(result)
        except Exception as exc:
            self.signals.failed.emit(str(exc))
        finally:
            self.signals.completed.emit()
