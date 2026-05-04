import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QIcon, QPixmap


def get_resource_path(filename: str) -> str:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        bundled = os.path.join(bundle_root, "imntlazy", "resources", filename)
        if os.path.exists(bundled):
            return bundled

    resource_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "resources", filename)
    )
    if os.path.exists(resource_path):
        return resource_path

    return ""


def make_icon() -> QIcon:
    icon = QIcon()
    ico_path = get_resource_path("app_icon.ico")
    png_path = get_resource_path("app_icon.png")

    if ico_path:
        icon.addFile(ico_path)
    if png_path:
        for size in (16, 20, 24, 32, 40, 48, 64, 128, 256):
            icon.addFile(png_path, QSize(size, size))

    if not icon.isNull():
        return icon
    return QIcon(QPixmap())


class Dashboard(QWidget):
    start_clicked = Signal()
    stop_clicked = Signal()
    pause_clicked = Signal()
    whitelist_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("I'm not lazy.")
        self.setMinimumSize(560, 500)
        self.resize(560, 500)
        self.setWindowIcon(make_icon())

        self._btn_pause: QPushButton | None = None
        self._btn_start: QPushButton | None = None
        self._btn_stop: QPushButton | None = None
        self._status_label: QLabel | None = None
        self._timer_label: QLabel | None = None
        self._status_badge: QLabel | None = None
        self._layout_synced = False

        self._build_ui()
        QTimer.singleShot(0, self._sync_layout)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addLayout(self._build_header())
        root.addWidget(self._build_hero_card())
        root.addWidget(self._build_actions_card())
        root.addWidget(self._build_tools_card())
        root.addStretch()

        self.setStyleSheet(self._global_style())

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(14)

        icon_label = QLabel()
        icon_label.setPixmap(make_icon().pixmap(44, 44))
        icon_label.setObjectName("headerIcon")

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("I'm not lazy.")
        title.setObjectName("titleLabel")

        subtitle = QLabel("把电脑留给重要的事，剩下的交给专注模式处理。")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        header.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)
        header.addLayout(title_col, 1)
        return header

    def _build_hero_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("heroCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        eyebrow = QLabel("当前状态")
        eyebrow.setObjectName("eyebrowLabel")

        self._status_badge = QLabel("待开始")
        self._status_badge.setObjectName("statusBadge")

        top_row.addWidget(eyebrow)
        top_row.addStretch()
        top_row.addWidget(self._status_badge)

        self._status_label = QLabel("空闲 — 等待开始专注")
        self._status_label.setObjectName("statusText")
        self._status_label.setWordWrap(True)

        self._timer_label = QLabel("点击“开始专注”进入专注模式")
        self._timer_label.setObjectName("timerText")
        self._timer_label.setWordWrap(True)

        helper = QLabel("关闭主窗口只会隐藏到托盘，不会退出程序。")
        helper.setObjectName("helperText")
        helper.setWordWrap(True)

        layout.addLayout(top_row)
        layout.addWidget(self._status_label)
        layout.addWidget(self._timer_label)
        layout.addWidget(helper)
        return card

    def _build_actions_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("panelCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)

        title = QLabel("快捷操作")
        title.setObjectName("sectionTitle")

        subtitle = QLabel("开始、暂停或结束当前专注流程。")
        subtitle.setObjectName("sectionSubtitle")

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        self._btn_start = QPushButton("开始专注")
        self._btn_start.setMinimumHeight(46)
        self._btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_start.setObjectName("primaryAction")
        self._btn_start.clicked.connect(self.start_clicked.emit)

        self._btn_pause = QPushButton("暂停")
        self._btn_pause.setMinimumHeight(46)
        self._btn_pause.setEnabled(False)
        self._btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_pause.setObjectName("secondaryAction")
        self._btn_pause.clicked.connect(self.pause_clicked.emit)

        self._btn_stop = QPushButton("停止")
        self._btn_stop.setMinimumHeight(46)
        self._btn_stop.setEnabled(False)
        self._btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_stop.setObjectName("dangerAction")
        self._btn_stop.clicked.connect(self.stop_clicked.emit)

        actions_row.addWidget(self._btn_start)
        actions_row.addWidget(self._btn_pause)
        actions_row.addWidget(self._btn_stop)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(actions_row)
        return card

    def _build_tools_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("panelCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)

        title = QLabel("辅助功能")
        title.setObjectName("sectionTitle")

        subtitle = QLabel("管理允许窗口、调整设置，或者把主窗口暂时收回托盘。")
        subtitle.setObjectName("sectionSubtitle")
        subtitle.setWordWrap(True)

        tools_row = QHBoxLayout()
        tools_row.setSpacing(10)

        btn_whitelist = QPushButton("允许窗口")
        btn_whitelist.setMinimumHeight(38)
        btn_whitelist.setObjectName("ghostAction")
        btn_whitelist.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_whitelist.clicked.connect(self.whitelist_clicked.emit)

        btn_settings = QPushButton("设置")
        btn_settings.setMinimumHeight(38)
        btn_settings.setObjectName("ghostAction")
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.clicked.connect(self.settings_clicked.emit)

        btn_tray = QPushButton("隐藏到托盘")
        btn_tray.setMinimumHeight(38)
        btn_tray.setObjectName("ghostAction")
        btn_tray.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tray.clicked.connect(self.hide)

        tools_row.addWidget(btn_whitelist)
        tools_row.addWidget(btn_settings)
        tools_row.addWidget(btn_tray)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(tools_row)
        return card

    def update_status(self, status: str, timer_text: str, in_session: bool):
        if self._status_label:
            self._status_label.setText(status)
        if self._timer_label:
            self._timer_label.setText(
                timer_text or ("计时准备中…" if in_session else "点击“开始专注”进入专注模式")
            )
        if self._btn_start:
            self._btn_start.setEnabled(not in_session)
        if self._btn_stop:
            self._btn_stop.setEnabled(in_session)
        if self._btn_pause:
            self._btn_pause.setEnabled(in_session)
        self._update_badge(status, in_session)

    def set_pause_text(self, text: str):
        if self._btn_pause:
            self._btn_pause.setText("暂停" if text == "暂停" else "恢复")

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._layout_synced:
            QTimer.singleShot(0, self._sync_layout)

    def _sync_layout(self):
        if self.layout():
            self.layout().activate()
        self.updateGeometry()
        self.adjustSize()
        self.resize(max(self.width(), 560), max(self.height(), 500))
        self._layout_synced = True

    def _update_badge(self, status: str, in_session: bool):
        if self._status_badge is None:
            return

        if "休息" in status:
            label = "休息中"
            bg = "rgba(236, 253, 245, 0.9)"
            fg = "#047857"
        elif "暂停" in status:
            label = "已暂停"
            bg = "rgba(255, 247, 237, 0.92)"
            fg = "#c2410c"
        elif in_session:
            label = "专注中"
            bg = "rgba(238, 242, 255, 0.92)"
            fg = "#4338ca"
        else:
            label = "待开始"
            bg = "rgba(255, 255, 255, 0.9)"
            fg = "#475569"

        self._status_badge.setText(label)
        self._status_badge.setStyleSheet(
            "padding: 6px 12px; border-radius: 999px; "
            f"background-color: {bg}; color: {fg}; font-weight: 600;"
        )

    @staticmethod
    def _global_style() -> str:
        return """
            QWidget {
                background-color: #f4f7fb;
                color: #0f172a;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#subtitleLabel {
                font-size: 13px;
                color: #64748b;
            }
            QLabel#eyebrowLabel {
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1px;
                color: rgba(255, 255, 255, 0.8);
                text-transform: uppercase;
            }
            QLabel#statusText {
                background: transparent;
                font-size: 22px;
                font-weight: 700;
                color: #ffffff;
            }
            QLabel#timerText {
                background: transparent;
                font-size: 30px;
                font-weight: 700;
                color: #e0f2fe;
            }
            QLabel#helperText {
                background: transparent;
                font-size: 12px;
                color: rgba(255, 255, 255, 0.84);
            }
            QLabel#sectionTitle {
                font-size: 16px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#sectionSubtitle {
                font-size: 12px;
                color: #64748b;
            }
            QFrame#heroCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #4338ca, stop: 0.55 #2563eb, stop: 1 #0891b2
                );
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 24px;
            }
            QFrame#panelCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 20px;
            }
            QPushButton {
                border-radius: 14px;
                padding: 10px 18px;
                border: 1px solid #dbe2ea;
                background-color: #ffffff;
                color: #1e293b;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: #c7d2fe;
                background-color: #f8fbff;
            }
            QPushButton:pressed {
                background-color: #eef2ff;
            }
            QPushButton:disabled {
                background-color: #f8fafc;
                color: #94a3b8;
                border-color: #e2e8f0;
            }
            QPushButton#primaryAction {
                border: none;
                color: #ffffff;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4f46e5, stop: 1 #2563eb
                );
            }
            QPushButton#primaryAction:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #5b52f0, stop: 1 #3175f5
                );
            }
            QPushButton#primaryAction:disabled {
                background: #c7d2fe;
                color: #eff6ff;
            }
            QPushButton#secondaryAction {
                background-color: #ffffff;
                border-color: #cbd5e1;
            }
            QPushButton#dangerAction {
                border: none;
                color: #ffffff;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ef4444, stop: 1 #f97316
                );
            }
            QPushButton#dangerAction:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #f35d5d, stop: 1 #fb8c3b
                );
            }
            QPushButton#dangerAction:disabled {
                background: #fecaca;
                color: #fff7ed;
            }
            QPushButton#ghostAction {
                background-color: #f8fafc;
                border-color: #e2e8f0;
            }
            QPushButton#ghostAction:hover {
                background-color: #eef2ff;
                border-color: #c7d2fe;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 6px 0 6px 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 32px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar:horizontal, QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal, QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }
        """
