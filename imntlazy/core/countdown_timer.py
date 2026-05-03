from PySide6.QtCore import QTimer, QObject, Signal


class CountdownTimer(QObject):
    tick = Signal(object)   # TimeSpan remaining
    expired = Signal()

    def __init__(self, duration_seconds: int, parent=None):
        super().__init__(parent)
        self._remaining = duration_seconds
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)
        self._is_paused = False
        self._is_running = False

    @property
    def remaining(self) -> int:
        return self._remaining

    def start(self):
        if self._is_running and not self._is_paused:
            return
        self._is_running = True
        self._is_paused = False
        self._timer.start()

    def pause(self):
        if not self._is_running or self._is_paused:
            return
        self._is_paused = True
        self._timer.stop()

    def resume(self):
        if not self._is_running or not self._is_paused:
            return
        self._is_paused = False
        self._timer.start()

    def stop(self):
        self._is_running = False
        self._is_paused = False
        self._timer.stop()

    def reset(self, duration_seconds: int):
        self.stop()
        self._remaining = duration_seconds

    def _on_tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._remaining = 0
            self._is_running = False
            self._timer.stop()

        self.tick.emit(self._remaining)

        if self._remaining <= 0:
            self.expired.emit()
