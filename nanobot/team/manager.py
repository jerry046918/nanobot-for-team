"""TeamManager: load, save, and query team membership."""

from __future__ import annotations

import json
from dataclasses import asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from nanobot.team.schema import TeamMember, TeamRegistry
from nanobot.utils.helpers import ensure_dir

if TYPE_CHECKING:
    pass

_REGISTRY_FILE = "team.json"


def _member_to_dict(m: TeamMember) -> dict:
    return {
        "nickname": m.nickname,
        "role": m.role,
        "channel_ids": m.channel_ids,
        "joined_at": m.joined_at,
        "invited_by": m.invited_by,
    }


def _member_from_dict(d: dict) -> TeamMember:
    return TeamMember(
        nickname=d["nickname"],
        role=d.get("role", "member"),
        channel_ids=d.get("channel_ids", {}),
        joined_at=d.get("joined_at", ""),
        invited_by=d.get("invited_by"),
    )


class TeamManager:
    """
    Manages team membership stored in {workspace}/team.json.

    Responsibilities:
    - Load/save team registry from disk.
    - Resolve an incoming (channel, sender_id) to a TeamMember.
    - Invite, update, and remove members.
    - Provide per-user workspace paths (USER.md, private sessions).
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self._registry_path = workspace / _REGISTRY_FILE
        self._registry: TeamRegistry | None = None

    # ------------------------------------------------------------------
    # Registry I/O
    # ------------------------------------------------------------------

    def _load(self) -> TeamRegistry:
        if not self._registry_path.exists():
            return TeamRegistry()
        try:
            data = json.loads(self._registry_path.read_text(encoding="utf-8"))
            members = [_member_from_dict(m) for m in data.get("members", [])]
            return TeamRegistry(version=data.get("version", 1), members=members)
        except Exception as e:
            logger.warning("Failed to load team registry: {}", e)
            return TeamRegistry()

    def _save(self) -> None:
        reg = self._registry or TeamRegistry()
        data = {
            "version": reg.version,
            "members": [_member_to_dict(m) for m in reg.members],
        }
        self._registry_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @property
    def registry(self) -> TeamRegistry:
        if self._registry is None:
            self._registry = self._load()
        return self._registry

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def resolve_member(self, channel: str, sender_id: str) -> TeamMember | None:
        """Return the TeamMember whose channel_ids[channel] matches sender_id, or None."""
        sid = str(sender_id)
        for m in self.registry.members:
            mapped = m.channel_ids.get(channel)
            if mapped and str(mapped) == sid:
                return m
        return None

    def get_member_by_nickname(self, nickname: str) -> TeamMember | None:
        """Look up a member by their global nickname (case-insensitive)."""
        nick = nickname.strip().lower()
        for m in self.registry.members:
            if m.nickname.lower() == nick:
                return m
        return None

    def list_members(self) -> list[TeamMember]:
        """Return all registered team members."""
        return list(self.registry.members)

    def is_admin(self, member: TeamMember | None) -> bool:
        return member is not None and member.role == "admin"

    def has_members(self) -> bool:
        return bool(self.registry.members)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def add_member(
        self,
        nickname: str,
        channel: str,
        sender_id: str,
        role: str = "member",
        invited_by: str | None = None,
    ) -> TeamMember:
        """Register a new team member. Raises ValueError if nickname already exists."""
        if self.get_member_by_nickname(nickname):
            raise ValueError(f"Nickname '{nickname}' is already taken.")
        now = datetime.now(timezone.utc).isoformat()
        member = TeamMember(
            nickname=nickname,
            role=role,  # type: ignore[arg-type]
            channel_ids={channel: str(sender_id)},
            joined_at=now,
            invited_by=invited_by,
        )
        self.registry.members.append(member)
        self._save()
        logger.info("Team member added: {} ({})", nickname, role)
        return member

    def bind_channel(self, nickname: str, channel: str, sender_id: str) -> TeamMember:
        """Add or update a channel→sender_id binding for an existing member."""
        member = self.get_member_by_nickname(nickname)
        if member is None:
            raise ValueError(f"No member with nickname '{nickname}'.")
        member.channel_ids[channel] = str(sender_id)
        self._save()
        logger.info("Bound {}/{} to {}", channel, sender_id, nickname)
        return member

    def set_role(self, nickname: str, role: str) -> TeamMember:
        """Change the role of an existing member."""
        member = self.get_member_by_nickname(nickname)
        if member is None:
            raise ValueError(f"No member with nickname '{nickname}'.")
        member.role = role  # type: ignore[assignment]
        self._save()
        logger.info("Role updated: {} -> {}", nickname, role)
        return member

    def remove_member(self, nickname: str) -> bool:
        """Remove a member by nickname. Returns True if removed."""
        nick = nickname.strip().lower()
        before = len(self.registry.members)
        self.registry.members = [m for m in self.registry.members if m.nickname.lower() != nick]
        if len(self.registry.members) < before:
            self._save()
            logger.info("Team member removed: {}", nickname)
            return True
        return False

    # ------------------------------------------------------------------
    # Per-user workspace paths
    # ------------------------------------------------------------------

    def user_dir(self, nickname: str) -> Path:
        """Return (and create) the workspace directory for a specific user."""
        d = self.workspace / "users" / nickname
        ensure_dir(d)
        return d

    def user_profile_path(self, nickname: str) -> Path:
        """Path to USER.md for this member."""
        return self.user_dir(nickname) / "USER.md"

    def user_sessions_dir(self, nickname: str) -> Path:
        """Path to private session storage for this member."""
        return ensure_dir(self.user_dir(nickname) / "sessions")

    def read_user_profile(self, nickname: str) -> str:
        """Read USER.md content for a member, or empty string if not present."""
        path = self.user_profile_path(nickname)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def write_user_profile(self, nickname: str, content: str) -> None:
        """Write USER.md for a member."""
        self.user_profile_path(nickname).write_text(content, encoding="utf-8")
