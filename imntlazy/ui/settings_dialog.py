from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QLabel, QSpinBox, QCheckBox, QPushButton,
    QFormLayout, QPlainTextEdit, QWidget,
)
from ..models import AppSettings


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("I'm not lazy. — 设置")
        self.setMinimumSize(560, 520)
        self.resize(560, 520)
        self.setModal(True)

        self._init_ui()
        self._load_values()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), "  常规  ")
        tabs.addTab(self._build_websites_tab(), "  网站屏蔽  ")
        tabs.addTab(self._build_exit_tab(), "  退出确认  ")
        tabs.addTab(self._build_face_tab(), "  人脸检测  ")
        root.addWidget(tabs)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = QPushButton("确定")
        btn_ok.setMinimumSize(100, 32)
        btn_ok.clicked.connect(self._save_and_accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.setMinimumSize(100, 32)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        root.addLayout(btn_row)

    def _build_general_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        gb = QGroupBox("时长设置")
        form = QFormLayout(gb)
        form.setSpacing(10)

        self._spin_total = QSpinBox()
        self._spin_total.setRange(5, 600)
        self._spin_total.setSuffix(" 分钟（到时间后自动结束）")
        form.addRow("专注总时长：", self._spin_total)

        self._spin_work = QSpinBox()
        self._spin_work.setRange(5, 120)
        self._spin_work.setSuffix(" 分钟")
        form.addRow("每段工作时长：", self._spin_work)

        self._spin_break = QSpinBox()
        self._spin_break.setRange(1, 60)
        self._spin_break.setSuffix(" 分钟（休息期间限制全部解除）")
        form.addRow("每段休息时长：", self._spin_break)

        layout.addWidget(gb)
        layout.addStretch()
        return w

    def _build_websites_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("专注模式期间禁止访问的域名（每行一个，无需 http:// 前缀）："))
        self._txt_domains = QPlainTextEdit()
        self._txt_domains.setMinimumHeight(300)
        layout.addWidget(self._txt_domains)
        note = QLabel("www 子域名会被自动一并屏蔽。修改在下次专注开始时生效。")
        note.setStyleSheet("color: #888;")
        layout.addWidget(note)
        return w

    def _build_exit_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("手动退出专注模式时必须输入的确认文本（区分大小写）："))
        self._txt_exit = QPlainTextEdit()
        self._txt_exit.setMaximumHeight(100)
        layout.addWidget(self._txt_exit)
        hint = QLabel("建议设置一句足够长的、能让你在放弃前三思的话。")
        hint.setStyleSheet("color: #888;")
        layout.addWidget(hint)
        layout.addStretch()
        return w

    def _build_face_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self._chk_face = QCheckBox(
            "启用摄像头人脸检测\n"
            "正常工作模式：每 1~2 秒检测一次，连续 10 次未检测到触发提醒（约 10~20 秒）。\n"
            "提醒触发后：切换为高速检测（每 0.5 秒），检测到人脸后立即关闭提醒。")
        self._chk_face.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._chk_face)

        gb_beep = QGroupBox("声音提醒")
        bform = QFormLayout(gb_beep)
        self._chk_beep = QCheckBox("触发提醒时同步发出蜂鸣声")
        bform.addRow(self._chk_beep)
        self._spin_beep = QSpinBox()
        self._spin_beep.setRange(1, 60)
        self._spin_beep.setSuffix(" 秒响一次")
        bform.addRow("蜂鸣间隔：每", self._spin_beep)
        layout.addWidget(gb_beep)

        layout.addStretch()
        return w

    def _load_values(self):
        s = self._settings
        self._spin_total.setValue(s.total_focus_duration_minutes)
        self._spin_work.setValue(s.work_duration_minutes)
        self._spin_break.setValue(s.break_duration_minutes)
        self._txt_domains.setPlainText("\n".join(s.blocked_domains))
        self._txt_exit.setPlainText(s.exit_confirmation_phrase)
        self._chk_face.setChecked(s.face_detection_enabled)
        self._chk_beep.setChecked(s.beep_on_alert)
        self._spin_beep.setValue(s.beep_interval_seconds)

    def _save_and_accept(self):
        s = self._settings
        s.total_focus_duration_minutes = self._spin_total.value()
        s.work_duration_minutes = self._spin_work.value()
        s.break_duration_minutes = self._spin_break.value()
        s.blocked_domains = [
            d.strip() for d in self._txt_domains.toPlainText().splitlines()
            if d.strip()
        ]
        s.exit_confirmation_phrase = self._txt_exit.toPlainText().strip()
        s.face_detection_enabled = self._chk_face.isChecked()
        s.beep_on_alert = self._chk_beep.isChecked()
        s.beep_interval_seconds = self._spin_beep.value()
        s.save()
        self.accept()
