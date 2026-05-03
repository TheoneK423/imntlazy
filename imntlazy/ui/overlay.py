from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from ..win32.input_blocker import InputBlocker


class Overlay(QWidget):
    """Fullscreen alert overlay with marching ants border and slow color pulse."""

    def __init__(self, beep_enabled: bool = True, beep_interval: int = 10):
        super().__init__()
        self._input_blocker = InputBlocker()
        self._frame_offset = 0
        self._beep_enabled = beep_enabled
        self._pulse_colors = [
            QColor(255, 191, 0),
            QColor(0, 255, 255),
            QColor(128, 0, 128),
        ]

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setCursor(Qt.CursorShape.BlankCursor)

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(33)
        self._anim_timer.timeout.connect(self._on_anim_tick)
        self._anim_timer.start()

        self._beep_timer: QTimer | None = None
        if beep_enabled:
            self._beep_timer = QTimer(self)
            self._beep_timer.setInterval(beep_interval * 1000)
            self._beep_timer.timeout.connect(self._beep)
            self._beep_timer.start()

    def showEvent(self, event):
        super().showEvent(event)
        self._input_blocker.install()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._input_blocker.uninstall()

    def _on_anim_tick(self):
        self._frame_offset = (self._frame_offset + 1) % 15
        self.update()

    def _beep(self):
        try:
            QApplication.beep()
        except Exception:
            pass

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        pulse = self._get_pulse_color()
        p.fillRect(rect, pulse)
        self._draw_marching_ants(p, rect)
        self._draw_center_text(p, rect)
        p.end()

    def _get_pulse_color(self) -> QColor:
        import time
        t = time.time() * 0.33
        phase = t % 3.0
        if phase < 1.0:
            return self._lerp_color(self._pulse_colors[0], self._pulse_colors[1], phase)
        elif phase < 2.0:
            return self._lerp_color(self._pulse_colors[1], self._pulse_colors[2], phase - 1.0)
        else:
            return self._lerp_color(self._pulse_colors[2], self._pulse_colors[0], phase - 2.0)

    @staticmethod
    def _lerp_color(a: QColor, b: QColor, t: float) -> QColor:
        return QColor(
            int(a.red() + (b.red() - a.red()) * t),
            int(a.green() + (b.green() - a.green()) * t),
            int(a.blue() + (b.blue() - a.blue()) * t),
        )

    def _draw_marching_ants(self, painter: QPainter, rect):
        bw = 15
        dash_pattern = [10, 5]
        r = rect.adjusted(bw // 2, bw // 2, -bw // 2, -bw // 2)

        pen_outer = QPen(Qt.GlobalColor.white, bw)
        pen_outer.setDashPattern(dash_pattern)
        pen_outer.setDashOffset(-self._frame_offset)
        pen_inner = QPen(Qt.GlobalColor.black, bw)
        pen_inner.setDashPattern(dash_pattern)
        pen_inner.setDashOffset(-self._frame_offset + 7.5)

        painter.setPen(pen_outer)
        painter.drawRect(r)
        painter.setPen(pen_inner)
        painter.drawRect(r)

    def _draw_center_text(self, painter: QPainter, rect):
        text = "用户离开电脑摸鱼了\n请提醒用户回来专心干活。"
        font = QFont("Microsoft YaHei", 28, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0, 128))
        painter.drawText(rect.adjusted(3, 3, 3, 3), Qt.AlignmentFlag.AlignCenter, text)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def closeEvent(self, event):
        self._anim_timer.stop()
        if self._beep_timer:
            self._beep_timer.stop()
        self._input_blocker.uninstall()
        super().closeEvent(event)
