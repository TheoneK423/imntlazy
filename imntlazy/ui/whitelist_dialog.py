from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from ..models import WhitelistEntry
from ..win32.window_enum import enumerate_visible_windows
from .dashboard import make_icon


class CheckableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pressed_item: QListWidgetItem | None = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed_item = self.itemAt(event.position().toPoint())
            if self._pressed_item is not None:
                self.setCurrentItem(self._pressed_item)
                event.accept()
                return
        self._pressed_item = None
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item is not None and item is self._pressed_item:
                next_state = (
                    Qt.CheckState.Unchecked
                    if item.checkState() == Qt.CheckState.Checked
                    else Qt.CheckState.Checked
                )
                item.setCheckState(next_state)
                self.setCurrentItem(item)
                self._pressed_item = None
                event.accept()
                return
        self._pressed_item = None
        super().mouseReleaseEvent(event)


class WhitelistDialog(QDialog):
    def __init__(self, current_whitelist: list[WhitelistEntry], parent=None):
        super().__init__(parent)
        self._all_windows: list[tuple[int, str, str]] = []
        self._selected_entries: list[WhitelistEntry] = []

        self.setWindowTitle("选择允许的窗口")
        self.setWindowIcon(make_icon())
        self.setMinimumSize(760, 620)
        self.resize(760, 620)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)

        layout.addWidget(self._build_header())

        helper = QLabel("勾选的窗口会在专注模式下保留，未勾选的窗口会被自动最小化。")
        helper.setObjectName("mutedLabel")
        helper.setWordWrap(True)
        layout.addWidget(helper)

        self._list = CheckableListWidget()
        self._list.setObjectName("windowList")
        self._list.setSpacing(6)
        layout.addWidget(self._list, 1)

        self._populate(current_whitelist)

        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(10)

        btn_refresh = QPushButton("刷新列表")
        btn_refresh.setObjectName("secondaryButton")
        btn_refresh.clicked.connect(lambda: self._populate(None))

        btn_select_all = QPushButton("全选")
        btn_select_all.setObjectName("secondaryButton")
        btn_select_all.clicked.connect(self._select_all)

        btn_deselect_all = QPushButton("取消全选")
        btn_deselect_all.setObjectName("secondaryButton")
        btn_deselect_all.clicked.connect(self._deselect_all)

        btn_row1.addWidget(btn_refresh)
        btn_row1.addWidget(btn_select_all)
        btn_row1.addWidget(btn_deselect_all)
        btn_row1.addStretch()
        layout.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        btn_row2.addStretch()

        btn_ok = QPushButton("保存选择")
        btn_ok.setMinimumSize(120, 40)
        btn_ok.setObjectName("primaryButton")
        btn_ok.clicked.connect(self._on_accept)

        btn_cancel = QPushButton("取消")
        btn_cancel.setMinimumSize(100, 40)
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)

        btn_row2.addWidget(btn_ok)
        btn_row2.addWidget(btn_cancel)
        layout.addLayout(btn_row2)

        self.setStyleSheet(self._dialog_style())

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("headerCard")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(6)

        title = QLabel("允许窗口名单")
        title.setObjectName("headerTitle")

        subtitle = QLabel("从当前可见窗口里挑出专注期间保留的目标。")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return header

    def _populate(self, existing_whitelist: list[WhitelistEntry] | None):
        self._list.clear()
        self._all_windows = enumerate_visible_windows()
        for _, title, pname in self._all_windows:
            text = f"[{pname}] {title}"
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checked = Qt.CheckState.Unchecked
            if existing_whitelist:
                for e in existing_whitelist:
                    if (e.window_title.lower() in title.lower() or
                        pname.lower() == e.process_name.lower()):
                        checked = Qt.CheckState.Checked
                        break
            item.setCheckState(checked)
            self._list.addItem(item)

    def _select_all(self):
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self):
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _on_accept(self):
        self._selected_entries.clear()
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.checkState() == Qt.CheckState.Checked and i < len(self._all_windows):
                _, title, pname = self._all_windows[i]
                self._selected_entries.append(WhitelistEntry(
                    window_title=title,
                    process_name=pname,
                    match_by_title=True,
                ))
        self.accept()

    @property
    def selected_entries(self) -> list[WhitelistEntry]:
        return self._selected_entries

    @staticmethod
    def _dialog_style() -> str:
        return """
            QDialog, QWidget {
                background-color: #f4f7fb;
                color: #0f172a;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QFrame#headerCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2563eb, stop: 1 #7c3aed
                );
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 22px;
            }
            QLabel#headerTitle {
                background: transparent;
                font-size: 22px;
                font-weight: 700;
                color: #ffffff;
            }
            QLabel#headerSubtitle {
                background: transparent;
                font-size: 13px;
                color: rgba(255, 255, 255, 0.86);
            }
            QLabel#mutedLabel {
                color: #64748b;
            }
            QListWidget#windowList {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 10px;
                outline: none;
            }
            QListWidget#windowList::item {
                background-color: #f8fafc;
                border: none;
                border-radius: 14px;
                padding: 12px 14px;
                margin: 2px 0;
            }
            QListWidget#windowList::item:hover {
                background-color: #eef2ff;
                border-color: #c7d2fe;
            }
            QListWidget#windowList::item:selected {
                background-color: #e0e7ff;
                border-color: #818cf8;
                color: #312e81;
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
            QPushButton#primaryButton {
                border: none;
                color: #ffffff;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4f46e5, stop: 1 #2563eb
                );
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #5b52f0, stop: 1 #3175f5
                );
            }
            QPushButton#secondaryButton {
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 8px 4px 8px 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 36px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }
        """
