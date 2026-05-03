from PySide6.QtCore import QTimer, QObject
from ..models import WhitelistEntry
from ..win32.window_enum import enumerate_visible_windows, minimize_window


class WindowRestrictor(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._whitelist: list[WhitelistEntry] = []
        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._enforce_once)
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    def load_whitelist(self, entries: list[WhitelistEntry]) -> None:
        self._whitelist = list(entries)

    def enable(self):
        if self._active:
            return
        self._active = True
        self._timer.start()

    def disable(self):
        self._active = False
        self._timer.stop()

    def enforce_once(self):
        self._enforce_once()

    def _enforce_once(self):
        if not self._active:
            return
        try:
            for hwnd, title, pname in enumerate_visible_windows():
                if not self._is_allowed(title, pname):
                    minimize_window(hwnd)
        except Exception:
            pass

    def _is_allowed(self, title: str, process_name: str) -> bool:
        for entry in self._whitelist:
            if entry.window_title and entry.window_title.lower() in title.lower():
                return True
            if entry.process_name and entry.process_name.lower() == process_name.lower():
                return True
        return False
