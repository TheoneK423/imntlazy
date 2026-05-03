from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
)
from PySide6.QtCore import Qt


class ExitConfirmDialog(QDialog):
    def __init__(self, required_phrase: str, parent=None):
        super().__init__(parent)
        self._phrase = required_phrase

        self.setWindowTitle("确认退出专注模式")
        self.setMinimumSize(580, 220)
        self.resize(580, 220)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel("要退出专注模式，请输入以下文字（不含引号）："))

        phrase_label = QLabel(f'"{required_phrase}"')
        phrase_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        phrase_label.setWordWrap(True)
        layout.addWidget(phrase_label)

        self._input = QLineEdit()
        self._input.setMinimumHeight(30)
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_ok = QPushButton("确认退出")
        self._btn_ok.setMinimumSize(100, 32)
        self._btn_ok.setEnabled(False)
        self._btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.setMinimumSize(100, 32)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self._btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def _on_text_changed(self):
        self._btn_ok.setEnabled(self._input.text().strip() == self._phrase.strip())
