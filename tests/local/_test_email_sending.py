from datetime import datetime
from pathlib import Path
from string import Template

from app.common.request_state_config import REQUEST_STATE_CONFIG
from app.infrastructure.email.templates import TEMPLATE_REGISTRY

LOG_FILE = Path(__file__).parents[2] / "dummy_print_email_sending.txt"


def test_request_email_config_logging():
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    with open(LOG_FILE, "w") as f:
        for from_status, transitions in REQUEST_STATE_CONFIG.items():
            for to_status, config in transitions.items():
                template_name = config.get("template")
                notify_roles = config.get("notify_roles", [])
                if not template_name:
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
                    email_body = template.substitute(
                        request_code="REQ-1",
                        request_title="Test Request",
                        user_name=f"{role.name}_User",
                        request_id=1,
                        request_type="Type > Subtype",
                        priority="Medium",
                        submitted_at=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
                        status=to_status.value,
                        link="http://frontend/requests/1",
                    )
                    f.write(
                        f"To: {role.name}_User\nSubject: {template_name}\n{email_body}\n"
                    )
                    f.write("-" * 50 + "\n")

    assert LOG_FILE.exists()
    print(LOG_FILE.read_text())
