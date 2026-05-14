"""Base class for platform messaging.

Every platform-specific messenger (email, eBay API, Facebook DM) must
subclass `Messenger` and implement send/poll. The negotiator uses these
without knowing which platform it's talking to.
"""

from abc import ABC, abstractmethod

from haggler.models.schemas import Message, Platform


class Messenger(ABC):
    """Abstract base class for sending and receiving messages."""

    platform: Platform

    @abstractmethod
    async def send(self, conversation_id: str, body: str) -> None:
        """Send a message in the given conversation.

        Args:
            conversation_id: Platform-specific conversation identifier.
            body: Plain text message body.

        Raises:
            MessengerError: When the message cannot be delivered.
        """
        ...

    @abstractmethod
    async def poll_replies(self, conversation_id: str) -> list[Message]:
        """Fetch any new seller replies since last poll.

        Args:
            conversation_id: Platform-specific conversation identifier.

        Returns:
            List of new messages from the seller, oldest first.
            Empty list if no new messages.
        """
        ...


class MessengerError(Exception):
    """Raised when a messenger fails to send or receive."""
