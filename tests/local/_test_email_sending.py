from datetime import datetime
from pathlib import Path
from string import Template
from types import SimpleNamespace

from app.common.request_state_config import REQUEST_STATE_CONFIG
from app.infrastructure.email.templates import TEMPLATE_REGISTRY

LOG_FILE = Path(__file__).parents[2] / "dummy_print_email_sending.txt"


def test_request_email_config_logging_realistic():
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    mock_request = SimpleNamespace(
        id=1,
        title="Test Request",
        type=SimpleNamespace(name="Type"),
        subtype=SimpleNamespace(name="Subtype"),
        priority=SimpleNamespace(value="Medium"),
        created_at=datetime.now(),
        current_status=None,
        requester=SimpleNamespace(
            email="requester@example.com", first_name="Requester", last_name="User"
        ),
        approver=SimpleNamespace(
            email="approver@example.com", first_name="Approver", last_name="User"
        ),
        admin=SimpleNamespace(
            email="admin@example.com", first_name="Admin", last_name="User"
        ),
    )

    with open(LOG_FILE, "w") as f:
        for from_status, transitions in REQUEST_STATE_CONFIG.items():
            for to_status, config in transitions.items():
                template_name = config.get("template")
                notify_roles = config.get("notify_roles", [])

                if not template_name or not notify_roles:
                    continue

                template: Template = TEMPLATE_REGISTRY.get(template_name)
                if not template:
                    f.write(f"Missing template for {from_status} -> {to_status}\n")
                    continue

                f.write("=" * 50 + "\n")
                f.write(
                    f"{from_status.value} -> {to_status.value} \n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write("=" * 50 + "\n")

                for role in notify_roles:
                    user_obj = getattr(mock_request, role.value.lower(), None)
                    if not user_obj or not getattr(user_obj, "email", None):
                        continue

                    email_body = template.substitute(
                        request_code=f"REQ-{mock_request.id}",
                        request_title=mock_request.title,
                        user_name=f"{user_obj.first_name} {user_obj.last_name}",
                        request_id=mock_request.id,
                        request_type=f"{mock_request.type.name} > {mock_request.subtype.name}",
                        priority=mock_request.priority.value,
                        submitted_at=mock_request.created_at.strftime(
                            "%B %d, %Y at %I:%M %p"
                        ),
                        status=to_status.value,
                        link=f"http://frontend/requests/{mock_request.id}",
                    )

                    f.write(
                        f"To: {user_obj.email}\nSubject: {template_name}\n{email_body}\n"
                    )
                    f.write("-" * 50 + "\n")

    assert LOG_FILE.exists()
    print(LOG_FILE.read_text())
