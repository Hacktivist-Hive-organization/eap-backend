# app/infrastructure/email/interfaces.py

from abc import ABC, abstractmethod
from typing import Sequence

from models import EmailMessage


class EmailServiceInterface(ABC):
    @abstractmethod
    async def send(self, message: EmailMessage) -> None:
        pass
