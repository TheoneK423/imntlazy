from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QLabel, QSpinBox, QCheckBox, QPushButton,
    QFormLayout, QPlainTextEdit, QWidget, QFrame,
)
from PySide6.QtCore import Qt
from ..models import AppSettings
from .dashboard import make_icon


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("I'm not lazy. — 设置")
        self.setWindowIcon(make_icon())
        self.setMinimumSize(700, 620)
        self.resize(700, 620)
        self.setModal(True)

        self._init_ui()
        self._load_values()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(16)

        root.addWidget(self._build_header())

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setObjectName("settingsTabs")
        self._tabs.tabBar().setDrawBase(False)
        self._tabs.addTab(self._build_general_tab(), "常规")
        self._tabs.addTab(self._build_websites_tab(), "网站屏蔽")
        self._tabs.addTab(self._build_exit_tab(), "退出确认")
        self._tabs.addTab(self._build_face_tab(), "人脸检测")
        root.addWidget(self._tabs)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_ok = QPushButton("保存设置")
        btn_ok.setMinimumSize(120, 40)
        btn_ok.setObjectName("primaryButton")
        btn_ok.clicked.connect(self._save_and_accept)

        btn_cancel = QPushButton("取消")
        btn_cancel.setMinimumSize(100, 40)
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        root.addLayout(btn_row)

        self.setStyleSheet(self._dialog_style())

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("headerCard")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(6)

        title = QLabel("偏好设置")
        title.setObjectName("headerTitle")

        subtitle = QLabel("集中管理专注时长、网站限制、退出确认和提醒行为。")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return header

    def _build_general_tab(self):
        w = QWidget()
        w.setObjectName("settingsPage")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(14)

        intro = QLabel("调整总时长以及每轮工作 / 休息节奏。")
        intro.setObjectName("mutedLabel")

        gb = QGroupBox("时长设置")
        form = QFormLayout(gb)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._spin_total = QSpinBox()
        self._spin_total.setRange(5, 600)
        self._spin_total.setSuffix(" 分钟")
        form.addRow("专注总时长", self._spin_total)

        self._spin_work = QSpinBox()
        self._spin_work.setRange(5, 120)
        self._spin_work.setSuffix(" 分钟")
        form.addRow("每段工作时长", self._spin_work)

        self._spin_break = QSpinBox()
        self._spin_break.setRange(1, 60)
        self._spin_break.setSuffix(" 分钟")
        form.addRow("每段休息时长", self._spin_break)

        note = QLabel("当总时长会落入一段休息时间时，软件会在该段休息开始时直接结束专注。")
        note.setObjectName("noteCard")
        note.setWordWrap(True)

        layout.addWidget(intro)
        layout.addWidget(gb)
        layout.addWidget(note)
        layout.addStretch()
        return w

    def _build_websites_tab(self):
        w = QWidget()
        w.setObjectName("settingsPage")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(14)

        intro = QLabel("这些域名会在专注模式开始时写入 hosts 进行本地拦截。")
        intro.setObjectName("mutedLabel")

        self._txt_domains = QPlainTextEdit()
        self._txt_domains.setMinimumHeight(320)
        self._txt_domains.setPlaceholderText("例如：\nzhihu.com\nbilibili.com\nyoutube.com")

        note = QLabel("每行一个域名，无需填写 http://。对应的 www 子域名也会一并屏蔽。")
        note.setObjectName("noteCard")
        note.setWordWrap(True)

        layout.addWidget(intro)
        layout.addWidget(self._txt_domains)
        layout.addWidget(note)
        return w

    def _build_exit_tab(self):
        w = QWidget()
        w.setObjectName("settingsPage")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(14)

        intro = QLabel("为了避免冲动结束专注，可以要求手动输入一段确认文本。")
        intro.setObjectName("mutedLabel")

        self._txt_exit = QPlainTextEdit()
        self._txt_exit.setMaximumHeight(140)
        self._txt_exit.setPlaceholderText("输入一段你愿意为退出专注承担后果的确认语")

        hint = QLabel("留空时，将允许直接确认退出。")
        hint.setObjectName("noteCard")
        hint.setWordWrap(True)

        layout.addWidget(intro)
        layout.addWidget(self._txt_exit)
        layout.addWidget(hint)
        layout.addStretch()
        return w

    def _build_face_tab(self):
        w = QWidget()
        w.setObjectName("settingsPage")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(14)

        self._chk_face = QCheckBox(
            "启用摄像头人脸检测\n"
            "正常工作模式：每 1 秒检测一次，连续约 10 秒未检测到则触发提醒。\n"
            "提醒触发后：切换为每 0.5 秒检测一次，检测到人脸后立即关闭提醒。"
        )
        self._chk_face.setObjectName("mainCheck")

        gb_beep = QGroupBox("声音提醒")
        bform = QFormLayout(gb_beep)
        bform.setSpacing(12)

        self._chk_beep = QCheckBox("触发提醒时同步发出蜂鸣声")
        bform.addRow(self._chk_beep)

        self._spin_beep = QSpinBox()
        self._spin_beep.setRange(1, 60)
        self._spin_beep.setSuffix(" 秒")
        bform.addRow("蜂鸣间隔", self._spin_beep)

        note = QLabel("这里只控制是否启用检测和提醒声音，检测节奏保持固定。")
        note.setObjectName("noteCard")
        note.setWordWrap(True)

        layout.addWidget(self._chk_face)
        layout.addWidget(gb_beep)
        layout.addWidget(note)
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
                    stop: 0 #1d4ed8, stop: 1 #0f766e
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
            QLabel#noteCard {
                background-color: #eef4ff;
                color: #334155;
                border: 1px solid #dbeafe;
                border-radius: 14px;
                padding: 12px 14px;
            }
            QWidget#settingsPage {
                background: transparent;
                border: none;
            }
            QTabWidget#settingsTabs {
                background: transparent;
                border: none;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
                top: 0px;
            }
            QTabBar {
                background: transparent;
                border: none;
            }
            QTabBar::tab-bar {
                alignment: left;
                left: 0px;
                border: none;
            }
            QTabBar::base {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.72);
                color: #64748b;
                padding: 10px 18px;
                margin-right: 6px;
                border-radius: 12px;
                border: 1px solid transparent;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                background: rgba(255, 255, 255, 0.95);
                color: #334155;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1e293b;
                border: 1px solid #e2e8f0;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #edf2f7;
                border-radius: 18px;
                margin-top: 16px;
                padding: 18px 16px 16px 16px;
                font-weight: 700;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #334155;
            }
            QSpinBox, QPlainTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px 10px;
                selection-background-color: #c7d2fe;
            }
            QSpinBox:focus, QPlainTextEdit:focus {
                border-color: #6366f1;
                background-color: #ffffff;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                subcontrol-origin: border;
                width: 22px;
                border: none;
                background: transparent;
                margin-right: 4px;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 8px;
                height: 8px;
            }
            QCheckBox {
                background: transparent;
                border: none;
                color: #0f172a;
                spacing: 8px;
                padding: 0;
            }
            QCheckBox#mainCheck {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 16px;
                font-weight: 600;
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
            QScrollBar:horizontal {
                background: transparent;
                height: 10px;
                margin: 0 8px 4px 8px;
            }
            QScrollBar::handle:horizontal {
                background: #cbd5e1;
                min-width: 36px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line, QScrollBar::sub-line,
            QScrollBar::add-page, QScrollBar::sub-page {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }
        """
