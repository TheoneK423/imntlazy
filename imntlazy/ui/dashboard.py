from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont


def make_icon() -> QIcon:
    """Generate programmatic app icon: white IM on blue circle."""
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(33, 150, 243))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4, 4, 56, 56)
    p.setPen(QColor(255, 255, 255))
    font = QFont("Microsoft YaHei", 22, QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "IM")
    p.end()
    return QIcon(pix)


class Dashboard(QWidget):
    start_clicked = Signal()
    stop_clicked = Signal()
    pause_clicked = Signal()
    whitelist_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("I'm not lazy.")
        self.setMinimumSize(420, 360)
        self.resize(420, 360)
        self.setWindowIcon(make_icon())

        self._btn_pause: QPushButton | None = None
        self._btn_start: QPushButton | None = None
        self._btn_stop: QPushButton | None = None
        self._status_label: QLabel | None = None
        self._timer_label: QLabel | None = None

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Title row
        title_row = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(make_icon().pixmap(32, 32))
        title = QLabel("I'm not lazy.")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")
        title_row.addWidget(icon_lbl)
        title_row.addWidget(title)
        title_row.addStretch()
        root.addLayout(title_row)

        # Status card
        gb_status = QGroupBox("当前状态")
        gb_status.setStyleSheet(self._card_style())
        status_layout = QVBoxLayout(gb_status)
        status_layout.setContentsMargins(16, 20, 16, 16)
        self._status_label = QLabel("空闲 — 等待开始专注")
        self._status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; border: none;")
        self._timer_label = QLabel("")
        self._timer_label.setStyleSheet("font-size: 28px; color: #1976D2; border: none;")
        self._timer_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self._status_label)
        status_layout.addWidget(self._timer_label)
        root.addWidget(gb_status)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        self._btn_start = QPushButton("  开始专注")
        self._btn_start.setMinimumHeight(42)
        self._btn_start.setCursor(Qt.PointingHandCursor)
        self._btn_start.clicked.connect(self.start_clicked.emit)

        self._btn_pause = QPushButton("  暂停")
        self._btn_pause.setMinimumHeight(42)
        self._btn_pause.setEnabled(False)
        self._btn_pause.setCursor(Qt.PointingHandCursor)
        self._btn_pause.clicked.connect(self.pause_clicked.emit)

        self._btn_stop = QPushButton("  停止")
        self._btn_stop.setMinimumHeight(42)
        self._btn_stop.setEnabled(False)
        self._btn_stop.setCursor(Qt.PointingHandCursor)
        self._btn_stop.clicked.connect(self.stop_clicked.emit)

        actions_layout.addWidget(self._btn_start)
        actions_layout.addWidget(self._btn_pause)
        actions_layout.addWidget(self._btn_stop)
        root.addLayout(actions_layout)

        # Tool buttons
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(8)

        btn_whitelist = QPushButton("选择允许的窗口")
        btn_whitelist.setMinimumHeight(30)
        btn_whitelist.setCursor(Qt.PointingHandCursor)
        btn_whitelist.clicked.connect(self.whitelist_clicked.emit)

        btn_settings = QPushButton("设置")
        btn_settings.setMinimumHeight(30)
        btn_settings.setCursor(Qt.PointingHandCursor)
        btn_settings.clicked.connect(self.settings_clicked.emit)

        btn_tray = QPushButton("隐藏到托盘")
        btn_tray.setMinimumHeight(30)
        btn_tray.setCursor(Qt.PointingHandCursor)
        btn_tray.clicked.connect(self.hide)

        tools_layout.addWidget(btn_whitelist)
        tools_layout.addWidget(btn_settings)
        tools_layout.addWidget(btn_tray)
        root.addLayout(tools_layout)

        self.setStyleSheet(self._global_style())

        # Apply object names for QSS selector matching
        self._btn_start.setObjectName("btnStart")
        self._btn_stop.setObjectName("btnStop")

    def update_status(self, status: str, timer_text: str, in_session: bool):
        self._status_label.setText(status)
        self._timer_label.setText(timer_text)
        self._btn_start.setEnabled(not in_session)
        self._btn_stop.setEnabled(in_session)
        self._btn_pause.setEnabled(in_session)

    def set_pause_text(self, text: str):
        if self._btn_pause:
            self._btn_pause.setText("  暂停" if text == "暂停" else "  恢复")

    def closeEvent(self, event):
        # Minimize to tray instead of closing
        self.hide()
        event.ignore()

    @staticmethod
    def _card_style() -> str:
        return """
            QGroupBox {
                background-color: #fff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 14px;
                padding-top: 18px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #555;
            }
        """

    @staticmethod
    def _global_style() -> str:
        return """
            QWidget {
                background-color: #f0f2f5;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QPushButton {
                background-color: #fff;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 16px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
            QPushButton:disabled {
                background-color: #eee;
                color: #aaa;
                border-color: #e0e0e0;
            }
            QPushButton#btnStart {
                background-color: #2196F3;
                color: #fff;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#btnStart:hover {
                background-color: #42a5f5;
            }
            QPushButton#btnStart:disabled {
                background-color: #bbdefb;
                color: #e3f2fd;
            }
            QPushButton#btnStop {
                background-color: #f44336;
                color: #fff;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#btnStop:hover {
                background-color: #ef5350;
            }
            QPushButton#btnStop:disabled {
                background-color: #ffcdd2;
                color: #ffebee;
            }
        """
