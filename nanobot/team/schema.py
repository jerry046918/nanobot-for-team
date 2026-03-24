"""Team data models for multi-user shared assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class TeamMember:
    """A registered member of the team."""

    nickname: str
    """Global nickname used across all channels (e.g. 'alice')."""

    role: Literal["admin", "member"] = "member"
    """admin can manage members and all cron jobs; member can use the assistant normally."""

    channel_ids: dict[str, str] = field(default_factory=dict)
    """Mapping of channel name -> sender_id (e.g. {'telegram': '1234567', 'slack': 'U012'})."""

    joined_at: str = ""
    """ISO-8601 timestamp when the member was added."""

    invited_by: str | None = None
    """Nickname of the admin who invited this member, or None if bootstrapped."""


@dataclass
class TeamRegistry:
    """Persistent store for team membership."""

    version: int = 1
    members: list[TeamMember] = field(default_factory=list)
