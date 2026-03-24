"""Event types for the message bus."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nanobot.team.schema import TeamMember


@dataclass
class InboundMessage:
    """Message received from a chat channel."""

    channel: str  # telegram, discord, slack, whatsapp
    sender_id: str  # User identifier
    chat_id: str  # Chat/channel identifier
    content: str  # Message text
    timestamp: datetime = field(default_factory=datetime.now)
    media: list[str] = field(default_factory=list)  # Media URLs
    metadata: dict[str, Any] = field(default_factory=dict)  # Channel-specific data
    session_key_override: str | None = None  # Optional override for thread-scoped sessions
    member: TeamMember | None = None  # Resolved team member, injected by BaseChannel

    @property
    def session_key(self) -> str:
        """Unique key for session identification."""
        if self.session_key_override:
            return self.session_key_override
        # Private DM sessions are scoped to the member nickname for isolation.
        if self.member and self._is_dm():
            return f"{self.channel}:user:{self.member.nickname}"
        return f"{self.channel}:{self.chat_id}"

    def _is_dm(self) -> bool:
        """True when the message is a direct/private conversation (not a group)."""
        return self.metadata.get("_is_dm", False)


@dataclass
class OutboundMessage:
    """Message to send to a chat channel."""

    channel: str
    chat_id: str
    content: str
    reply_to: str | None = None
    media: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


