from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QMessageBox
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer
from .ui.dashboard import Dashboard, make_icon
from .models import AppSettings, FocusState
from .core.window_restrictor import WindowRestrictor
from .core.website_blocker import WebsiteBlocker
from .core.face_detector import FaceDetector
from .core.focus_session import FocusSession
from .ui.settings_dialog import SettingsDialog
from .ui.whitelist_dialog import WhitelistDialog
from .ui.exit_confirm import ExitConfirmDialog
from .ui.overlay import Overlay


class ImntlazyApp:
    def __init__(self):
        self._settings = AppSettings.load()
        self._window_restrictor = WindowRestrictor()
        self._website_blocker = WebsiteBlocker()
        self._face_detector = FaceDetector(self._settings)
        self._session: FocusSession | None = None
        self._overlay: Overlay | None = None
        self._dashboard: Dashboard | None = None
        self._stop_dialog: ExitConfirmDialog | None = None
        self._stop_requested = False

        self._window_restrictor.load_whitelist(self._settings.whitelisted_windows)
        self._website_blocker.load_domains(self._settings.blocked_domains)
        self._website_blocker.unblock()

        self._face_detector.face_detected.connect(self._on_face_detected)
        self._face_detector.face_lost.connect(self._on_face_lost)

        self._icon = make_icon()
        QApplication.instance().setWindowIcon(self._icon)

        self._tray = QSystemTrayIcon()
        self._tray.setIcon(self._icon)
        self._tray.setToolTip("I'm not lazy. — 空闲")
        self._tray.setContextMenu(self._build_tray_menu())
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

        self._dashboard = Dashboard()
        self._dashboard.start_clicked.connect(self._on_start)
        self._dashboard.stop_clicked.connect(self._on_stop)
        self._dashboard.pause_clicked.connect(self._on_pause_resume)
        self._dashboard.whitelist_clicked.connect(self._open_whitelist)
        self._dashboard.settings_clicked.connect(self._open_settings)
        self._dashboard.show()

    # ── Tray menu ─────────────────────────────────────────────────────

    def _build_tray_menu(self) -> QMenu:
        menu = QMenu()
        menu.setObjectName("trayMenu")
        menu.setStyleSheet(self._tray_menu_style())

        self._act_status = menu.addAction("I'm not lazy. — 空闲")
        self._act_status.setEnabled(False)
        menu.addSeparator()

        self._act_start = menu.addAction("开始专注")
        self._act_start.triggered.connect(self._on_start)

        self._act_pause = menu.addAction("暂停")
        self._act_pause.setEnabled(False)
        self._act_pause.triggered.connect(self._on_pause_resume)

        self._act_stop = menu.addAction("停止专注")
        self._act_stop.setEnabled(False)
        self._act_stop.triggered.connect(self._on_stop)

        menu.addSeparator()
        menu.addAction("打开主窗口").triggered.connect(self._show_dashboard)
        menu.addAction("设置").triggered.connect(self._open_settings)
        menu.addSeparator()
        menu.addAction("退出").triggered.connect(self._exit_app)

        return menu

    @staticmethod
    def _tray_menu_style() -> str:
        return """
            QMenu {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 16px;
                padding: 8px;
                color: #e2e8f0;
            }
            QMenu::item {
                padding: 10px 18px;
                margin: 2px 4px;
                border-radius: 10px;
                background-color: transparent;
                color: #e2e8f0;
            }
            QMenu::item:selected {
                background-color: #2563eb;
                color: #ffffff;
            }
            QMenu::item:disabled {
                background-color: #111c31;
                color: #93a4bd;
                font-weight: 600;
            }
            QMenu::separator {
                height: 1px;
                margin: 6px 10px;
                background-color: #22304a;
            }
        """

    # ── Actions ───────────────────────────────────────────────────────

    def _on_start(self):
        if self._session is not None and self._session.current_state not in (
            FocusState.IDLE, FocusState.ENDED
        ):
            self._tray.showMessage("imntlazy", "专注模式已在运行中。",
                                   QSystemTrayIcon.MessageIcon.Information, 3000)
            return

        self._window_restrictor.load_whitelist(self._settings.whitelisted_windows)
        self._website_blocker.load_domains(self._settings.blocked_domains)

        if not self._settings.whitelisted_windows:
            result = QMessageBox.warning(
                None, "I'm not lazy.",
                "你还没有选择任何允许的窗口。是否现在选择？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if result == QMessageBox.StandardButton.Yes:
                self._open_whitelist()
            if not self._settings.whitelisted_windows:
                return

        self._session = FocusSession(
            self._window_restrictor, self._website_blocker, self._settings
        )
        self._session.state_changed.connect(self._on_state_changed)
        self._session.timer_tick.connect(self._on_timer_tick)

        total_sec = self._settings.total_focus_duration_minutes * 60
        self._session.start(total_sec)
        self._face_detector.start_monitoring()

        self._tray.showMessage("imntlazy",
            f"专注模式已启动（总时长 {self._settings.total_focus_duration_minutes} 分钟）",
            QSystemTrayIcon.MessageIcon.Information, 3000,
        )

    def _on_stop(self):
        if self._session is None or self._session.current_state in (
            FocusState.IDLE, FocusState.ENDED
        ):
            return
        if self._stop_dialog is not None:
            self._stop_dialog.raise_()
            self._stop_dialog.activateWindow()
            return

        self._show_dashboard()

        dlg = ExitConfirmDialog(self._settings.exit_confirmation_phrase, self._dashboard)
        dlg.accepted.connect(self._request_stop)
        dlg.finished.connect(self._clear_stop_dialog)
        self._stop_dialog = dlg
        dlg.open()

    def _request_stop(self):
        self._stop_requested = True
        QTimer.singleShot(0, self._finalize_stop_request)

    def _clear_stop_dialog(self):
        if self._stop_dialog is not None:
            self._stop_dialog.deleteLater()
            self._stop_dialog = None

    def _finalize_stop_request(self):
        if not self._stop_requested:
            return
        self._stop_requested = False
        if self._session is None or self._session.current_state in (
            FocusState.IDLE, FocusState.ENDED
        ):
            return
        self._session.force_stop(emit_state=False)
        self._complete_stop_flow()
        self._tray.showMessage("imntlazy", "专注模式已结束。",
                               QSystemTrayIcon.MessageIcon.Information, 3000)

    def _on_pause_resume(self):
        if self._session is None:
            return
        if self._session.current_state == FocusState.WORKING:
            self._session.pause()
        elif self._session.current_state == FocusState.PAUSED:
            self._session.resume()

    def _quick_duration(self, minutes: int):
        self._settings.total_focus_duration_minutes = minutes
        self._settings.save()

    def _open_whitelist(self):
        dlg = WhitelistDialog(self._settings.whitelisted_windows)
        if dlg.exec() == WhitelistDialog.DialogCode.Accepted:
            self._settings.whitelisted_windows = list(dlg.selected_entries)
            self._settings.save()
            self._window_restrictor.load_whitelist(self._settings.whitelisted_windows)

    def _open_settings(self):
        dlg = SettingsDialog(self._settings)
        if dlg.exec() == SettingsDialog.DialogCode.Accepted:
            self._window_restrictor.load_whitelist(self._settings.whitelisted_windows)
            self._website_blocker.load_domains(self._settings.blocked_domains)

    def _show_dashboard(self):
        if not self._dashboard:
            return

        self._dashboard.showNormal()
        self._dashboard.show()
        self._dashboard.raise_()
        self._dashboard.activateWindow()

    def _exit_app(self):
        if self._session:
            self._session.force_stop()
        self._face_detector.release()
        if self._overlay:
            self._overlay.close()
        self._website_blocker.unblock()
        if self._dashboard:
            self._dashboard.hide()
        QApplication.quit()

    # ── Tray activation ───────────────────────────────────────────────

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_dashboard()

    # ── Face detection ────────────────────────────────────────────────

    def _on_face_lost(self):
        if self._overlay is None:
            self._face_detector.set_urgent(True)
            self._overlay = Overlay(
                self._settings.beep_on_alert,
                self._settings.beep_interval_seconds,
            )
            self._overlay.show()

    def _on_face_detected(self):
        self._face_detector.set_urgent(False)
        if self._overlay:
            self._overlay.close()
            self._overlay = None

    # ── Session state ─────────────────────────────────────────────────

    def _on_state_changed(self, state: FocusState):
        ds = self._dashboard

        if state == FocusState.WORKING:
            self._update_tray_state("专注中", True)
            self._act_pause.setText("暂停")
            self._act_pause.setEnabled(True)
            self._face_detector.start_monitoring()
            if ds:
                ds.update_status("专注中", "", True)
                ds.set_pause_text("暂停")
        elif state == FocusState.BREAK:
            self._update_tray_state("休息中", True)
            self._act_pause.setEnabled(False)
            self._face_detector.stop_monitoring()
            self._on_face_detected()  # dismiss overlay if shown
            if ds:
                ds.update_status("休息中 — 自由使用电脑", "", True)
            self._tray.showMessage("imntlazy", "休息时间！自由使用电脑。",
                                   QSystemTrayIcon.MessageIcon.Information, 3000)
        elif state == FocusState.PAUSED:
            self._update_tray_state("已暂停", True)
            self._act_pause.setText("恢复")
            if ds:
                ds.update_status("已暂停", "", True)
                ds.set_pause_text("恢复")
        elif state == FocusState.ENDED:
            self._complete_stop_flow()
            self._tray.showMessage("imntlazy", "专注模式已结束。",
                                   QSystemTrayIcon.MessageIcon.Information, 3000)

    def _complete_stop_flow(self):
        cleanup_error = self._session.last_cleanup_error if self._session else None
        self._update_tray_state("空闲", False)
        self._act_pause.setText("暂停")
        self._face_detector.stop_monitoring()
        self._on_face_detected()
        if self._dashboard:
            self._dashboard.update_status("空闲 — 等待开始专注", "", False)
            self._dashboard.set_pause_text("暂停")
        self._session = None
        self._tray.show()
        self._show_dashboard()
        QTimer.singleShot(0, self._show_dashboard)
        if cleanup_error:
            self._tray.showMessage(
                "imntlazy",
                f"专注已停止，但清理网站屏蔽时出错：{cleanup_error}",
                QSystemTrayIcon.MessageIcon.Warning,
                5000,
            )

    def _on_timer_tick(self, state: FocusState, remaining: int):
        mins = remaining // 60
        secs = remaining % 60
        ts = f"{mins:02d}:{secs:02d}"
        label = "工作" if state == FocusState.WORKING else "休息"
        tooltip = f"I'm not lazy. — {label} {ts}"
        self._tray.setToolTip(tooltip)
        self._act_status.setText(tooltip)

        if self._dashboard:
            status = "专注中" if state == FocusState.WORKING else "休息中"
            self._dashboard.update_status(status, f"剩余 {ts}", True)

    def _update_tray_state(self, status: str, in_session: bool):
        self._tray.setToolTip(f"I'm not lazy. — {status}")
        self._act_status.setText(f"I'm not lazy. — {status}")
        self._act_start.setEnabled(not in_session)
        self._act_stop.setEnabled(in_session)
        self._act_pause.setEnabled(in_session)
