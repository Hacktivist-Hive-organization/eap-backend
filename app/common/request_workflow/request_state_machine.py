# app/common/request_workflow/request_state_machine.py

from app.common.enums import Status
from app.common.request_workflow.request_state_config import REQUEST_STATE_CONFIG


class RequestStateMachine:

    @staticmethod
    def get_rule(current_status: Status, next_status: Status):
        transitions = REQUEST_STATE_CONFIG.get(current_status)
        if not transitions:
            return None
        return transitions.get(next_status)
