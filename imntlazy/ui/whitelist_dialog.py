from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem,
)
from PySide6.QtCore import Qt
from ..models import WhitelistEntry
from ..win32.window_enum import enumerate_visible_windows


class WhitelistDialog(QDialog):
    def __init__(self, current_whitelist: list[WhitelistEntry], parent=None):
        super().__init__(parent)
        self._all_windows: list[tuple[int, str, str]] = []
        self._selected_entries: list[WhitelistEntry] = []

        self.setWindowTitle("选择允许的窗口")
        self.setMinimumSize(680, 500)
        self.resize(680, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel(
            "勾选在专注模式下允许使用的窗口（未勾选的窗口将被自动最小化）："
        ))

        self._list = QListWidget()
        self._list.setStyleSheet("font-size: 13px;")
        # Allow individual checkbox toggling via click
        self._list.itemClicked.connect(self._toggle_item)
        layout.addWidget(self._list)

        self._populate(current_whitelist)

        # Buttons row 1: list manipulation
        btn_row1 = QHBoxLayout()
        btn_refresh = QPushButton("刷新列表")
        btn_refresh.clicked.connect(lambda: self._populate(None))
        btn_select_all = QPushButton("全选")
        btn_select_all.clicked.connect(self._select_all)
        btn_deselect_all = QPushButton("取消全选")
        btn_deselect_all.clicked.connect(self._deselect_all)
        btn_row1.addWidget(btn_refresh)
        btn_row1.addWidget(btn_select_all)
        btn_row1.addWidget(btn_deselect_all)
        btn_row1.addStretch()
        layout.addLayout(btn_row1)

        # Buttons row 2: OK/Cancel
        btn_row2 = QHBoxLayout()
        btn_row2.addStretch()
        btn_ok = QPushButton("确定")
        btn_ok.setMinimumSize(100, 32)
        btn_ok.clicked.connect(self._on_accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.setMinimumSize(100, 32)
        btn_cancel.clicked.connect(self.reject)
        btn_row2.addWidget(btn_ok)
        btn_row2.addWidget(btn_cancel)
        layout.addLayout(btn_row2)

    def _populate(self, existing_whitelist: list[WhitelistEntry] | None):
        self._list.clear()
        self._all_windows = enumerate_visible_windows()
        for hwnd, title, pname in self._all_windows:
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

    def _toggle_item(self, item: QListWidgetItem):
        new_state = Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
        item.setCheckState(new_state)

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
