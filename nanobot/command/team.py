"""Team management slash commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nanobot.bus.events import OutboundMessage
from nanobot.command.router import CommandContext, CommandRouter

if TYPE_CHECKING:
    from nanobot.team.manager import TeamManager


def _get_team_manager(ctx: CommandContext) -> TeamManager | None:
    """Extract TeamManager from the agent loop, if available."""
    loop = ctx.loop
    return getattr(loop, "team_manager", None) if loop else None


def _reply(ctx: CommandContext, text: str) -> OutboundMessage:
    return OutboundMessage(
        channel=ctx.msg.channel,
        chat_id=ctx.msg.chat_id,
        content=text,
        metadata={"render_as": "text"},
    )


async def cmd_invite(ctx: CommandContext) -> OutboundMessage:
    """/invite <nickname> <channel>:<sender_id> — Admin: register a new team member."""
    tm = _get_team_manager(ctx)
    if tm is None:
        return _reply(ctx, "Team mode is not enabled.")

    invoker = getattr(ctx.msg, "member", None)
    if not tm.is_admin(invoker):
        return _reply(ctx, "Only admins can invite members.")

    parts = ctx.args.strip().split()
    if len(parts) != 2 or ":" not in parts[1]:
        return _reply(ctx, "Usage: /invite <nickname> <channel>:<sender_id>")

    nickname = parts[0]
    channel_part, sender_id = parts[1].split(":", 1)

    try:
        member = tm.add_member(
            nickname=nickname,
            channel=channel_part,
            sender_id=sender_id,
            role="member",
            invited_by=invoker.nickname if invoker else None,
        )
        return _reply(ctx, f"Invited {member.nickname} as member on {channel_part}.")
    except ValueError as e:
        return _reply(ctx, str(e))


async def cmd_team(ctx: CommandContext) -> OutboundMessage:
    """/team — List all team members."""
    tm = _get_team_manager(ctx)
    if tm is None:
        return _reply(ctx, "Team mode is not enabled.")

    members = tm.list_members()
    if not members:
        return _reply(ctx, "No team members registered yet.")

    lines = ["Team members:"]
    for m in members:
        channels = ", ".join(f"{ch}:{sid}" for ch, sid in m.channel_ids.items()) or "(none)"
        lines.append(f"  {m.nickname} [{m.role}] — {channels}")
    return _reply(ctx, "\n".join(lines))


async def cmd_promote(ctx: CommandContext) -> OutboundMessage:
    """/promote <nickname> — Admin: promote a member to admin."""
    tm = _get_team_manager(ctx)
    if tm is None:
        return _reply(ctx, "Team mode is not enabled.")

    invoker = getattr(ctx.msg, "member", None)
    if not tm.is_admin(invoker):
        return _reply(ctx, "Only admins can promote members.")

    nickname = ctx.args.strip()
    if not nickname:
        return _reply(ctx, "Usage: /promote <nickname>")

    try:
        tm.set_role(nickname, "admin")
        return _reply(ctx, f"{nickname} is now an admin.")
    except ValueError as e:
        return _reply(ctx, str(e))


async def cmd_demote(ctx: CommandContext) -> OutboundMessage:
    """/demote <nickname> — Admin: demote an admin to member."""
    tm = _get_team_manager(ctx)
    if tm is None:
        return _reply(ctx, "Team mode is not enabled.")

    invoker = getattr(ctx.msg, "member", None)
    if not tm.is_admin(invoker):
        return _reply(ctx, "Only admins can demote members.")

    nickname = ctx.args.strip()
    if not nickname:
        return _reply(ctx, "Usage: /demote <nickname>")

    try:
        tm.set_role(nickname, "member")
        return _reply(ctx, f"{nickname} is now a regular member.")
    except ValueError as e:
        return _reply(ctx, str(e))


async def cmd_kick(ctx: CommandContext) -> OutboundMessage:
    """/kick <nickname> — Admin: remove a member from the team."""
    tm = _get_team_manager(ctx)
    if tm is None:
        return _reply(ctx, "Team mode is not enabled.")

    invoker = getattr(ctx.msg, "member", None)
    if not tm.is_admin(invoker):
        return _reply(ctx, "Only admins can kick members.")

    nickname = ctx.args.strip()
    if not nickname:
        return _reply(ctx, "Usage: /kick <nickname>")

    if tm.remove_member(nickname):
        return _reply(ctx, f"{nickname} has been removed from the team.")
    return _reply(ctx, f"No member named '{nickname}' found.")


async def cmd_bind(ctx: CommandContext) -> OutboundMessage:
    """/bind <nickname> <channel>:<sender_id> — Admin: add a new channel binding for an existing member."""
    tm = _get_team_manager(ctx)
    if tm is None:
        return _reply(ctx, "Team mode is not enabled.")

    invoker = getattr(ctx.msg, "member", None)
    if not tm.is_admin(invoker):
        return _reply(ctx, "Only admins can add channel bindings.")

    parts = ctx.args.strip().split()
    if len(parts) != 2 or ":" not in parts[1]:
        return _reply(ctx, "Usage: /bind <nickname> <channel>:<sender_id>")

    nickname = parts[0]
    channel_part, sender_id = parts[1].split(":", 1)

    try:
        tm.bind_channel(nickname, channel_part, sender_id)
        return _reply(ctx, f"Bound {channel_part}:{sender_id} to {nickname}.")
    except ValueError as e:
        return _reply(ctx, str(e))


async def cmd_profile(ctx: CommandContext) -> OutboundMessage:
    """/profile — Show your own USER.md profile content."""
    tm = _get_team_manager(ctx)
    if tm is None:
        return _reply(ctx, "Team mode is not enabled.")

    member = getattr(ctx.msg, "member", None)
    if member is None:
        return _reply(ctx, "You are not registered as a team member.")

    content = tm.read_user_profile(member.nickname)
    if not content:
        return _reply(ctx, f"No profile found for {member.nickname} yet.")
    return _reply(ctx, f"Profile for {member.nickname}:\n\n{content}")


def register_team_commands(router: CommandRouter) -> None:
    """Register team management slash commands."""
    router.prefix("/invite ", cmd_invite)
    router.exact("/team", cmd_team)
    router.prefix("/promote ", cmd_promote)
    router.prefix("/demote ", cmd_demote)
    router.prefix("/kick ", cmd_kick)
    router.prefix("/bind ", cmd_bind)
    router.exact("/profile", cmd_profile)
