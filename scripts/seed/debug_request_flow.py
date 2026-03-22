import sys
from pathlib import Path

# ----------------------------
# Ensure BE folder in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.common.enums import Status, UserRole
from app.common.request_workflow.request_state_config import REQUEST_STATE_CONFIG
from app.common.request_workflow.request_state_machine import RequestStateMachine
from app.common.request_workflow.request_transition_validator import (
    RequestTransitionValidator,
)

# ----------------------------
from app.database.session import SessionLocal
from app.models.db_request import DBRequest
from app.repositories.request_repository import RequestRepository
from app.repositories.user_repository import UserRepository


# ----------------------------
def print_transition(
    transition_name,
    owner,
    before_status,
    before_user_id,
    before_user_role,
    after_status,
    after_user_id,
    after_user_role,
):
    print(f"Transition: {transition_name}")
    print(f"Requester: {owner}")
    print("----")
    print(f"Status before: {before_status}")
    print(f"Assigned user ID before: {before_user_id}")
    print(f"Assigned user role before: {before_user_role}")
    print("----")
    print(f"Status after: {after_status}")
    print(f"Assigned user ID after: {after_user_id}")
    print(f"Assigned user role after: {after_user_role}")
    print("=" * 50)


# ----------------------------
def get_assigned_user(request, users, required_roles):
    """
    Determine assigned user for this request based on roles.
    For REQUESTER → always request.requester.
    For APPROVER → user assigned to request type.
    For ADMIN → any admin user.
    """
    for role in required_roles:
        if role == UserRole.REQUESTER:
            return request.requester
        elif role == UserRole.APPROVER:
            # Find user with APPROVER role and assigned to request type
            for u in users:
                if (
                    u.role == UserRole.APPROVER
                    and request.type_id in u.assigned_request_type_ids
                ):
                    return u
        elif role == UserRole.ADMIN:
            # Any admin
            for u in users:
                if u.role == UserRole.ADMIN:
                    return u
    return None


# ----------------------------
def process_request(db, request, users, validator, repo, state_machine):
    owner = request.requester.email if request.requester else "-"
    current_request = request

    while True:
        current_status = current_request.current_status
        possible_transitions = REQUEST_STATE_CONFIG.get(current_status)
        if not possible_transitions:
            break

        for next_status, rule in possible_transitions.items():
            transition_name = f"{current_status.value} → {next_status.value}"

            before_status = current_status.value
            before_assignee = current_request.assignee
            before_user_id = before_assignee.id if before_assignee else "-"
            before_user_role = before_assignee.role.value if before_assignee else "-"

            # Determine acting user from database according to rules
            acting_user = get_assigned_user(current_request, users, rule["roles"])
            if not acting_user:
                print(f"Transition {transition_name} skipped: no eligible user")
                continue

            # Apply transition with comment
            try:
                validator.validate(
                    current_request,
                    next_status,
                    acting_user.id,
                    comment=f"{transition_name}",
                )
                repo.update_request_status(current_request, next_status)
            except Exception as e:
                print(f"Transition {transition_name} failed: {e}")
                continue

            after_status = current_request.current_status.value
            after_user_id = acting_user.id
            after_user_role = acting_user.role.value

            print_transition(
                transition_name,
                owner,
                before_status,
                before_user_id,
                before_user_role,
                after_status,
                after_user_id,
                after_user_role,
            )

            # Move to next status
            current_request = repo.get_request_details(current_request.id)


# ----------------------------
def main():
    db = SessionLocal()
    user_repo = UserRepository(db)
    req_repo = RequestRepository(db)
    validator = RequestTransitionValidator(req_repo)
    state_machine = RequestStateMachine()

    users = user_repo.get_all_users()
    all_requests = db.query(DBRequest).order_by(DBRequest.id).all()

    if not all_requests:
        print("No requests found.")
        return

    # Process each request for scenarios
    for request in all_requests:
        print(
            f"\nPROCESSING REQUEST ID {request.id}, Requester: {request.requester.email}"
        )
        print("=" * 50)
        process_request(db, request, users, validator, req_repo, state_machine)

    db.close()


if __name__ == "__main__":
    main()
