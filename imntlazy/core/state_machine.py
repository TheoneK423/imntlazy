from ..models import FocusState


class FocusStateMachine:
    def __init__(self):
        self.current_state = FocusState.IDLE

    def can_transition(self, next_state: FocusState) -> bool:
        cs = self.current_state
        transitions = {
            FocusState.IDLE:    [FocusState.WORKING],
            FocusState.WORKING: [FocusState.BREAK, FocusState.PAUSED, FocusState.ENDED],
            FocusState.BREAK:   [FocusState.WORKING, FocusState.ENDED],
            FocusState.PAUSED:  [FocusState.WORKING],
            FocusState.ENDED:   [],
        }
        return next_state in transitions.get(cs, [])

    def set_state(self, state: FocusState):
        if not self.can_transition(state):
            raise ValueError(f"Invalid transition: {self.current_state} -> {state}")
        self.current_state = state
