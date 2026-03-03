from abc import ABC, abstractmethod


class NotificationSender(ABC):

    @abstractmethod
    async def send(self, text: str) -> None:
            ...
