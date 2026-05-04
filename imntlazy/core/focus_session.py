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
        self._current_timer = CountdownTimer(0, self)
        self._current_timer.tick.connect(self._on_timer_tick_internal)
        self._current_timer.expired.connect(self._on_timer_expired_internal)
        self._current_phase_duration = 0
        self._total_elapsed = 0  # seconds
        self._total_duration = 0  # seconds
        self._last_cleanup_error: OSError | None = None
        self._phase_state: FocusState | None = None
        self._phase_expired_handler = None

    @property
    def current_state(self) -> FocusState:
        return self._state_machine.current_state

    @property
    def last_cleanup_error(self) -> OSError | None:
        return self._last_cleanup_error

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

    def force_stop(self, emit_state: bool = True):
        self._clear_timer()
        self._last_cleanup_error = None
        try:
            self._website_blocker.unblock()
        except OSError as exc:
            self._last_cleanup_error = exc
        self._window_restrictor.disable()
        if emit_state:
            self._transition(FocusState.ENDED)
        else:
            self._state_machine.current_state = FocusState.ENDED

    # ── internals ──

    def _start_work_timer(self):
        self._start_phase_timer(
            FocusState.WORKING,
            min(self._settings.work_duration_minutes * 60, self._remaining_total()),
            self._on_work_expired,
        )

    def _on_work_expired(self):
        self._finish_current_phase()
        remaining = self._remaining_total()
        break_duration = self._settings.break_duration_minutes * 60
        if remaining <= 0 or remaining <= break_duration:
            self.force_stop()
            return

        self._website_blocker.unblock()
        self._window_restrictor.disable()
        self._transition(FocusState.BREAK)
        self._start_break_timer()

    def _start_break_timer(self):
        self._start_phase_timer(
            FocusState.BREAK,
            self._settings.break_duration_minutes * 60,
            self._on_break_expired,
        )

    def _on_break_expired(self):
        self._finish_current_phase()
        if self._remaining_total() <= 0:
            self.force_stop()
            return
        self._website_blocker.block()
        self._window_restrictor.enable()
        self._transition(FocusState.WORKING)
        self._start_work_timer()

    def _start_phase_timer(self, state: FocusState, duration: int, on_expired):
        if duration <= 0:
            self.force_stop()
            return

        self._clear_timer()
        self._phase_state = state
        self._phase_expired_handler = on_expired
        self._current_phase_duration = duration
        self._current_timer.reset(duration)
        self._current_timer.start()

    def _finish_current_phase(self):
        self._total_elapsed = min(
            self._total_duration,
            self._total_elapsed + self._current_phase_duration,
        )
        self._clear_timer()

    def _remaining_total(self) -> int:
        return max(0, self._total_duration - self._total_elapsed)

    def _clear_timer(self):
        self._current_timer.stop()
        self._phase_state = None
        self._phase_expired_handler = None
        self._current_phase_duration = 0

    def _on_timer_tick_internal(self, remaining: int):
        if self._phase_state is not None:
            self.timer_tick.emit(self._phase_state, remaining)

    def _on_timer_expired_internal(self):
        if self._phase_expired_handler is not None:
            self._phase_expired_handler()

    def _transition(self, state: FocusState):
        try:
            self._state_machine.set_state(state)
            self.state_changed.emit(state)
        except ValueError:
            pass
