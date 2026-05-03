from PySide6.QtCore import QObject, Signal
from ..models import FocusState, AppSettings
from .state_machine import FocusStateMachine
from .countdown_timer import CountdownTimer
from .window_restrictor import WindowRestrictor
from .website_blocker import WebsiteBlocker


class FocusSession(QObject):
    state_changed = Signal(FocusState)
    timer_tick = Signal(FocusState, int)  # state, remaining_seconds

    def __init__(
        self,
        window_restrictor: WindowRestrictor,
        website_blocker: WebsiteBlocker,
        settings: AppSettings,
        parent=None,
    ):
        super().__init__(parent)
        self._state_machine = FocusStateMachine()
        self._window_restrictor = window_restrictor
        self._website_blocker = website_blocker
        self._settings = settings
        self._current_timer: CountdownTimer | None = None
        self._total_elapsed = 0  # seconds
        self._total_duration = 0  # seconds

    @property
    def current_state(self) -> FocusState:
        return self._state_machine.current_state

    def start(self, total_seconds: int):
        if not self._state_machine.can_transition(FocusState.WORKING):
            return
        self._total_duration = total_seconds
        self._total_elapsed = 0

        self._website_blocker.block()
        self._window_restrictor.enable()

        self._transition(FocusState.WORKING)
        self._start_work_timer()

    def pause(self):
        if self._state_machine.can_transition(FocusState.PAUSED):
            if self._current_timer:
                self._current_timer.pause()
            self._transition(FocusState.PAUSED)

    def resume(self):
        if self._state_machine.can_transition(FocusState.WORKING):
            if self._current_timer:
                self._current_timer.resume()
            self._transition(FocusState.WORKING)

    def force_stop(self):
        if self._current_timer:
            self._current_timer.stop()
            self._current_timer = None
        self._website_blocker.unblock()
        self._window_restrictor.disable()
        self._transition(FocusState.ENDED)

    # ── internals ──

    def _start_work_timer(self):
        dur = self._settings.work_duration_minutes * 60
        self._current_timer = CountdownTimer(dur, self)
        self._current_timer.tick.connect(
            lambda r: self.timer_tick.emit(FocusState.WORKING, r))
        self._current_timer.expired.connect(self._on_work_expired)
        self._current_timer.start()

    def _on_work_expired(self):
        self._total_elapsed += self._settings.work_duration_minutes * 60
        if self._total_elapsed + self._settings.work_duration_minutes * 60 < self._total_duration:
            self._website_blocker.unblock()
            self._window_restrictor.disable()
            self._transition(FocusState.BREAK)
            self._start_break_timer()
        else:
            self.force_stop()

    def _start_break_timer(self):
        dur = self._settings.break_duration_minutes * 60
        self._current_timer = CountdownTimer(dur, self)
        self._current_timer.tick.connect(
            lambda r: self.timer_tick.emit(FocusState.BREAK, r))
        self._current_timer.expired.connect(self._on_break_expired)
        self._current_timer.start()

    def _on_break_expired(self):
        self._total_elapsed += self._settings.break_duration_minutes * 60
        if self._total_elapsed >= self._total_duration:
            self.force_stop()
            return
        self._website_blocker.block()
        self._window_restrictor.enable()
        self._transition(FocusState.WORKING)
        self._start_work_timer()

    def _transition(self, state: FocusState):
        try:
            self._state_machine.set_state(state)
            self.state_changed.emit(state)
        except ValueError:
            pass
