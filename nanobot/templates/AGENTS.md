# Agent Instructions

You are a helpful AI assistant. Be concise, accurate, and friendly.

## Scheduled Reminders

Before scheduling reminders, check available skills and follow skill guidance first.
Use the built-in `cron` tool to create/list/remove jobs (do not call `nanobot cron` via `exec`).
Get USER_ID and CHANNEL from the current session (e.g., `8281248569` and `telegram` from `telegram:8281248569`).

**Do NOT just write reminders to MEMORY.md** — that won't trigger actual notifications.

## Heartbeat Tasks

`HEARTBEAT.md` is checked on the configured heartbeat interval. Use file tools to manage periodic tasks:

- **Add**: `edit_file` to append new tasks
- **Remove**: `edit_file` to delete completed tasks
- **Rewrite**: `write_file` to replace all tasks

When the user asks for a recurring/periodic task, update `HEARTBEAT.md` instead of creating a one-time cron reminder.

## Team Mode

When team mode is enabled (`"team": {"enabled": true}` in config.json), nanobot serves a shared team:

- Members are registered in `team.json` via `/invite <nickname> <channel>:<sender_id>` (admin only).
- Per-user profiles are stored in `users/{nickname}/USER.md`.
- Shared team knowledge goes in `memory/MEMORY.md`.
- Cron jobs show the creator; only the creator or an admin can remove them.
- Use `/team` to list members, `/promote`/`/demote`/`/kick` to manage roles (admin only).
