#

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class EmailAttachment:
    filename: str
    content: bytes
    content_type: str


@dataclass(frozen=True)
class EmailMessage:
    subject: str
    recipients: Sequence[str]
    body: str
    sender: Optional[str] = None
    attachments: Sequence[EmailAttachment] = ()
