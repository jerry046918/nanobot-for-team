<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="500">
  <h1>nanobot: Ultra-Lightweight AI Assistant for Teams</h1>
  <p>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

**nanobot** is an ultra-lightweight AI assistant framework with **Team Mode** and a built-in **WebUI admin dashboard**. Deploy once, share across your entire team — every member gets recognized identity, private sessions, personal memory, and role-based access control.

## Key Features

- **Ultra-Lightweight** — Core agent in minimal code, fast startup, low resource usage
- **Team Mode** — Multi-user identity, per-member profiles, private sessions, role management (admin/member), dual-layer memory (shared + personal)
- **WebUI Dashboard** — Browser-based admin for chat, config editing, team management, and skill management
- **13+ Chat Channels** — Telegram, Discord, Slack, Feishu, DingTalk, WeChat, WhatsApp, WeCom, QQ, Matrix, Email, Mochat
- **20+ LLM Providers** — OpenRouter, OpenAI, Anthropic, DeepSeek, Ollama, vLLM, Azure, and more
- **MCP Support** — Connect external tool servers via Model Context Protocol (stdio + HTTP)
- **Skills System** — Extend agent capabilities with SKILL.md plugins; auto-loaded from workspace or built-in
- **Cron & Heartbeat** — Scheduled tasks and periodic self-checking via natural language
- **Built-in Tools** — File I/O, shell exec, web search & fetch, subagent spawning

## Architecture

<p align="center">
  <img src="nanobot_arch.png" alt="nanobot architecture" width="800">
</p>

## Table of Contents

- [Install](#-install)
- [Quick Start](#-quick-start)
- [WebUI Dashboard](#-webui-dashboard)
- [Team Mode](#-team-mode)
- [Chat Channels](#-chat-channels)
- [Configuration](#️-configuration)
- [CLI Reference](#-cli-reference)
- [Multiple Instances](#-multiple-instances)
- [Docker](#-docker)
- [Linux Service](#-linux-service)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

## 📦 Install

> [!NOTE]
> This is the **Team Edition** of nanobot. Install from source.

```bash
git clone https://github.com/jerry046918/nanobot-for-team.git
cd nanobot-for-team
pip install -e .
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -e .
```

### Update

```bash
cd nanobot-for-team
git pull
pip install -e .
```

## 🚀 Quick Start

**1. Initialize**

```bash
nanobot onboard
```

Use `nanobot onboard --wizard` for interactive setup.

**2. Configure** (`~/.nanobot/config.json`)

Set your API key (e.g. OpenRouter):

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "provider": "openrouter"
    }
  }
}
```

**3. Chat**

```bash
nanobot agent
```

That's it — you have a working AI assistant.

## 🖥️ WebUI Dashboard

nanobot includes a built-in web admin dashboard powered by FastAPI. Manage everything from your browser — no need to edit config files or use CLI for routine operations.

### Start

```bash
# Terminal 1 — start the gateway
nanobot gateway

# Terminal 2 — generate a login URL
nanobot webui
```

This prints a URL like `http://localhost:18791/?token=xxx`. Open it in your browser.

### Features

| Feature | Description |
|---------|-------------|
| **Chat** | Real-time conversation with the agent via WebSocket |
| **Config** | Visual configuration management — view and edit all settings |
| **Skills** | Browse, create, delete, and import skills (ZIP upload) |
| **Team** | Manage team members — add, edit roles, bind channels, remove |

### Configuration

```json
{
  "webui": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 18791,
    "token_ttl_hours": 24
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `true` | Enable/disable the WebUI server |
| `host` | `0.0.0.0` | Listen address |
| `port` | `18791` | Listen port |
| `token_ttl_hours` | `24` | Login token validity period |

### Security

- Token-based authentication — `nanobot webui` generates a time-limited login URL
- Session cookies with `HttpOnly` and `SameSite=Lax` flags
- Tokens stored as bcrypt hashes (never in plaintext)
- WebSocket connections validated against session
- Origin header checked on WebSocket upgrade
- Skill name validation prevents path traversal in WebUI APIs

## 👥 Team Mode

Team Mode lets a whole team share one nanobot instance. Each member is recognized by their nickname across all channels, has a private conversation session, and a personal profile (`USER.md`) that nanobot learns over time. Shared knowledge goes into team memory (`MEMORY.md`).

### How It Works

| Feature | Description |
|---------|-------------|
| **Member identity** | Each message is matched to a registered nickname via channel sender ID |
| **DM isolation** | Private messages use per-user sessions (`users/{nickname}/sessions/`) |
| **Dual-layer memory** | Shared team facts in `memory/MEMORY.md`; personal context in `users/{nickname}/USER.md` |
| **Role system** | `admin` — can invite, kick, promote; `member` — uses the assistant normally |
| **Cron ownership** | Cron jobs record the creator; only the creator or an admin can delete them |
| **WebUI management** | Full team CRUD via the WebUI dashboard |

### Setup

**1. Enable Team Mode** in `~/.nanobot/config.json`:

```json
{
  "team": {
    "enabled": true
  }
}
```

**2. Start the gateway**

```bash
nanobot gateway
```

**3. Bootstrap the first admin**

Create `~/.nanobot/workspace/team.json`:

```json
{
  "version": 1,
  "members": [
    {
      "nickname": "alice",
      "role": "admin",
      "channel_ids": { "telegram": "YOUR_TELEGRAM_USER_ID" },
      "joined_at": "2026-01-01T00:00:00+00:00",
      "invited_by": null
    }
  ]
}
```

> **Tip:** Find any user's sender ID in nanobot logs — it is printed when the first message arrives.

**4. Invite more members** (as admin, via chat)

```
/invite bob telegram:123456789
```

**5. Bind additional channels** (optional)

```
/bind bob slack:U012AB3CD
```

### Team Slash Commands

| Command | Who | Description |
|---------|-----|-------------|
| `/team` | Everyone | List all team members and their channel bindings |
| `/invite <nickname> <channel>:<id>` | Admin | Register a new member |
| `/bind <nickname> <channel>:<id>` | Admin | Add a channel binding for an existing member |
| `/promote <nickname>` | Admin | Grant admin role |
| `/demote <nickname>` | Admin | Revoke admin role |
| `/kick <nickname>` | Admin | Remove a member |
| `/profile` | Everyone | View your own `USER.md` profile |

### Workspace Layout (Team Mode)

```
~/.nanobot/workspace/
├── team.json                    # member registry
├── memory/
│   ├── MEMORY.md                # shared team long-term memory
│   └── HISTORY.md               # shared conversation history log
├── users/
│   ├── alice/
│   │   ├── USER.md              # alice's personal profile (auto-learned)
│   │   └── sessions/            # alice's private DM sessions
│   └── bob/
│       ├── USER.md
│       └── sessions/
├── cron/
│   └── jobs.json                # scheduled jobs (with creator field)
└── skills/                      # shared team skills
```

### Memory Consolidation

When a conversation is archived (token limit reached or `/new`), nanobot automatically:

- Writes **team-relevant** facts (projects, decisions, shared context) to `memory/MEMORY.md`
- Writes **user-specific** facts (preferences, work style, skills) to `users/{nickname}/USER.md`

Both files are injected into the system prompt for every message — the team memory for everyone, the personal profile only for the sender.

### Heartbeat Notifications (Team Mode)

Pin specific members to always receive heartbeat results:

```json
{
  "gateway": {
    "heartbeat": {
      "enabled": true,
      "intervalS": 1800,
      "notify": ["alice", "bob"]
    }
  }
}
```

## 💬 Chat Channels

Connect nanobot to your favorite chat platform. Want to build your own? See the [Channel Plugin Guide](./docs/CHANNEL_PLUGIN_GUIDE.md).

| Channel | What you need |
|---------|---------------|
| **Telegram** | Bot token from @BotFather |
| **Discord** | Bot token + Message Content intent |
| **WhatsApp** | QR code scan (`nanobot channels login whatsapp`) |
| **WeChat** | QR code scan (`nanobot channels login weixin`) |
| **Feishu** | App ID + App Secret |
| **DingTalk** | App Key + App Secret |
| **Slack** | Bot token + App-Level token |
| **Matrix** | Homeserver URL + Access token |
| **Email** | IMAP/SMTP credentials |
| **QQ** | App ID + App Secret |
| **WeCom** | Bot ID + Bot Secret |
| **Mochat** | Claw token (auto-setup available) |

<details>
<summary><b>Telegram</b> (Recommended)</summary>

**1. Create a bot** — Open Telegram, search `@BotFather`, send `/newbot`, copy the token.

**2. Configure**

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

**3. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Discord</b></summary>

**1. Create a bot** — Go to https://discord.com/developers/applications, create an app, add a Bot, copy the token.

**2. Enable intents** — In Bot settings, enable **MESSAGE CONTENT INTENT**.

**3. Configure**

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"],
      "groupPolicy": "mention"
    }
  }
}
```

> `groupPolicy`: `"mention"` (default) — respond only when @mentioned; `"open"` — respond to all messages.

**4. Invite the bot** — OAuth2 → URL Generator → Scopes: `bot` → Permissions: `Send Messages`, `Read Message History`.

**5. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Feishu (飞书)</b></summary>

Uses **WebSocket** long connection — no public IP required.

**1. Create a Feishu bot** — Visit [Feishu Open Platform](https://open.feishu.cn/app), create app, enable Bot capability, add `im:message` and `im:message.p2p_msg:readonly` permissions, add `im.message.receive_v1` event with Long Connection mode.

**2. Configure**

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "allowFrom": ["ou_YOUR_OPEN_ID"],
      "groupPolicy": "mention"
    }
  }
}
```

**3. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Slack</b></summary>

Uses **Socket Mode** — no public URL required.

**1. Create a Slack app** — [Slack API](https://api.slack.com/apps) → Create New App → From scratch.

**2. Configure the app** — Enable Socket Mode (generate App-Level Token with `connections:write`), add bot scopes (`chat:write`, `reactions:write`, `app_mentions:read`), enable Event Subscriptions (`message.im`, `message.channels`, `app_mention`), install app to workspace.

**3. Configure nanobot**

```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "botToken": "xoxb-...",
      "appToken": "xapp-...",
      "allowFrom": ["YOUR_SLACK_USER_ID"],
      "groupPolicy": "mention"
    }
  }
}
```

**4. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>WhatsApp</b></summary>

Requires **Node.js ≥18**.

**1. Link device**

```bash
nanobot channels login whatsapp
# Scan QR with WhatsApp → Settings → Linked Devices
```

**2. Configure**

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**3. Run** (two terminals)

```bash
# Terminal 1
nanobot channels login whatsapp

# Terminal 2
nanobot gateway
```

</details>

<details>
<summary><b>DingTalk (钉钉)</b></summary>

Uses **Stream Mode** — no public IP required.

**1. Create a DingTalk bot** — [DingTalk Open Platform](https://open-dev.dingtalk.com/), create app, add Robot capability, enable Stream Mode, get AppKey and AppSecret.

**2. Configure**

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "clientId": "YOUR_APP_KEY",
      "clientSecret": "YOUR_APP_SECRET",
      "allowFrom": ["YOUR_STAFF_ID"]
    }
  }
}
```

**3. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>WeChat (微信 / Weixin)</b></summary>

Uses HTTP long-poll with QR-code login. No local WeChat desktop client required.

**1. Install**

```bash
pip install -e ".[weixin]"
```

**2. Login**

```bash
nanobot channels login weixin
```

**3. Configure**

```json
{
  "channels": {
    "weixin": {
      "enabled": true,
      "allowFrom": ["YOUR_WECHAT_USER_ID"]
    }
  }
}
```

**4. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>WeCom (企业微信)</b></summary>

Uses **WebSocket** — no public IP required.

**1. Install**

```bash
pip install -e ".[wecom]"
```

**2. Create a WeCom AI Bot** — WeCom admin console → Intelligent Robot → Create Robot → API mode with long connection. Copy Bot ID and Secret.

**3. Configure**

```json
{
  "channels": {
    "wecom": {
      "enabled": true,
      "botId": "your_bot_id",
      "secret": "your_bot_secret",
      "allowFrom": ["your_id"]
    }
  }
}
```

**4. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>QQ</b></summary>

Uses **botpy SDK** with WebSocket. Currently supports private messages only.

**1. Register & create bot** — [QQ Open Platform](https://q.qq.com), create bot, copy AppID and AppSecret.

**2. Configure**

```json
{
  "channels": {
    "qq": {
      "enabled": true,
      "appId": "YOUR_APP_ID",
      "secret": "YOUR_APP_SECRET",
      "allowFrom": ["YOUR_OPENID"],
      "msgFormat": "plain"
    }
  }
}
```

**3. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Matrix (Element)</b></summary>

Install Matrix dependencies first:

```bash
pip install nanobot-ai[matrix]
```

**1. Get credentials** — You need `userId`, `accessToken`, and `deviceId` from your Matrix homeserver.

**2. Configure**

```json
{
  "channels": {
    "matrix": {
      "enabled": true,
      "homeserver": "https://matrix.org",
      "userId": "@nanobot:matrix.org",
      "accessToken": "syt_xxx",
      "deviceId": "NANOBOT01",
      "e2eeEnabled": true,
      "allowFrom": ["@your_user:matrix.org"],
      "groupPolicy": "open"
    }
  }
}
```

**3. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Email</b></summary>

nanobot polls **IMAP** for incoming mail and replies via **SMTP**.

**1. Get credentials** — Create a dedicated email account, enable 2FA, generate an App Password.

**2. Configure**

```json
{
  "channels": {
    "email": {
      "enabled": true,
      "consentGranted": true,
      "imapHost": "imap.gmail.com",
      "imapPort": 993,
      "imapUsername": "my-nanobot@gmail.com",
      "imapPassword": "your-app-password",
      "smtpHost": "smtp.gmail.com",
      "smtpPort": 587,
      "smtpUsername": "my-nanobot@gmail.com",
      "smtpPassword": "your-app-password",
      "fromAddress": "my-nanobot@gmail.com",
      "allowFrom": ["your-real-email@gmail.com"]
    }
  }
}
```

**3. Run**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Mochat (Claw IM)</b></summary>

Uses **Socket.IO WebSocket** by default, with HTTP polling fallback.

**1. Auto-setup** — Send this to nanobot:

```
Read https://raw.githubusercontent.com/HKUDS/MoChat/refs/heads/main/skills/nanobot/skill.md and register on MoChat. My Email account is xxx@xxx. Bind me as your owner and DM me on MoChat.
```

nanobot will register, configure, and connect automatically.

**2. Restart**

```bash
nanobot gateway
```

</details>

## ⚙️ Configuration

Config file: `~/.nanobot/config.json`

### Providers

| Provider | Get API Key |
|----------|-------------|
| `openrouter` (recommended) | [openrouter.ai](https://openrouter.ai) |
| `openai` | [platform.openai.com](https://platform.openai.com) |
| `anthropic` | [console.anthropic.com](https://console.anthropic.com) |
| `deepseek` | [platform.deepseek.com](https://platform.deepseek.com) |
| `azure_openai` | [portal.azure.com](https://portal.azure.com) |
| `gemini` | [aistudio.google.com](https://aistudio.google.com) |
| `groq` | [console.groq.com](https://console.groq.com) |
| `minimax` | [platform.minimaxi.com](https://platform.minimaxi.com) |
| `moonshot` | [platform.moonshot.cn](https://platform.moonshot.cn) |
| `dashscope` (Qwen) | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| `zhipu` (GLM) | [open.bigmodel.cn](https://open.bigmodel.cn) |
| `siliconflow` | [siliconflow.cn](https://siliconflow.cn) |
| `aihubmix` | [aihubmix.com](https://aihubmix.com) |
| `volcengine` | [volcengine.com](https://www.volcengine.com) |
| `mistral` | [docs.mistral.ai](https://docs.mistral.ai/) |
| `ollama` (local) | — |
| `vllm` (local) | — |
| `ovms` (local, Intel GPU) | — |
| `custom` (any OpenAI-compatible) | — |
| `openai_codex` (OAuth) | `nanobot provider login openai-codex` |
| `github_copilot` (OAuth) | `nanobot provider login github-copilot` |

<details>
<summary><b>Custom Provider (Any OpenAI-compatible API)</b></summary>

Connects directly to any OpenAI-compatible endpoint — LM Studio, llama.cpp, Together AI, etc. Model name is passed as-is.

```json
{
  "providers": {
    "custom": {
      "apiKey": "your-api-key",
      "apiBase": "https://api.your-provider.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "your-model-name"
    }
  }
}
```

> For local servers that don't require a key, set `apiKey` to any non-empty string (e.g. `"no-key"`).

</details>

<details>
<summary><b>Ollama (local)</b></summary>

```bash
ollama run llama3.2
```

```json
{
  "providers": {
    "ollama": {
      "apiBase": "http://localhost:11434"
    }
  },
  "agents": {
    "defaults": {
      "provider": "ollama",
      "model": "llama3.2"
    }
  }
}
```

</details>

<details>
<summary><b>vLLM (local)</b></summary>

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --port 8000
```

```json
{
  "providers": {
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://localhost:8000/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "meta-llama/Llama-3.1-8B-Instruct"
    }
  }
}
```

</details>

<details>
<summary><b>Adding a New Provider (Developer Guide)</b></summary>

Adding a provider takes **2 steps**:

**Step 1.** Add a `ProviderSpec` to `PROVIDERS` in `nanobot/providers/registry.py`:

```python
ProviderSpec(
    name="myprovider",
    keywords=("myprovider", "mymodel"),
    env_key="MYPROVIDER_API_KEY",
    display_name="My Provider",
    litellm_prefix="myprovider",
    skip_prefixes=("myprovider/",),
)
```

**Step 2.** Add a field to `ProvidersConfig` in `nanobot/config/schema.py`:

```python
class ProvidersConfig(BaseModel):
    ...
    myprovider: ProviderConfig = ProviderConfig()
```

</details>

### Web Search

nanobot supports multiple web search providers. Configure under `tools.web.search`.

| Provider | Config | Free |
|----------|--------|------|
| `brave` (default) | `apiKey` | No |
| `tavily` | `apiKey` | No |
| `jina` | `apiKey` | Free tier (10M tokens) |
| `searxng` | `baseUrl` | Yes (self-hosted) |
| `duckduckgo` | — | Yes |

When credentials are missing, nanobot automatically falls back to DuckDuckGo.

**Example (Brave):**

```json
{
  "tools": {
    "web": {
      "search": {
        "provider": "brave",
        "apiKey": "BSA..."
      }
    }
  }
}
```

**Example (DuckDuckGo, zero config):**

```json
{
  "tools": {
    "web": {
      "search": {
        "provider": "duckduckgo"
      }
    }
  }
}
```

> Use `proxy` to route all web requests through a proxy:
> ```json
> { "tools": { "web": { "proxy": "http://127.0.0.1:7890" } } }
> ```

### MCP (Model Context Protocol)

Connect external tool servers and use them as native agent tools. Config format is compatible with Claude Desktop / Cursor.

```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
      },
      "my-remote-mcp": {
        "url": "https://example.com/mcp/",
        "headers": { "Authorization": "Bearer xxxxx" }
      }
    }
  }
}
```

| Mode | Config | Example |
|------|--------|---------|
| **Stdio** | `command` + `args` | Local process via `npx` / `uvx` |
| **HTTP** | `url` + `headers` (optional) | Remote endpoint |

Use `toolTimeout` to override the default 30s per-call timeout, and `enabledTools` to register only a subset of tools from an MCP server.

### Security

| Option | Default | Description |
|--------|---------|-------------|
| `tools.restrictToWorkspace` | `false` | Restrict all agent tools to the workspace directory |
| `tools.exec.enable` | `true` | When `false`, disable shell command execution entirely |
| `channels.*.allowFrom` | `[]` (deny all) | Whitelist of user IDs. Use `["*"]` to allow everyone. |

**Built-in protections:**
- **SSRF protection**: All outbound web requests validate resolved IPs against private/internal ranges
- **Path traversal**: Filesystem tools enforce workspace boundaries; WebUI APIs validate paths
- **Config permissions**: `config.json` is saved with owner-only read/write permissions (`0o600`)
- **WebUI auth**: Token-based login with `HttpOnly`, `SameSite=Lax` session cookies; tokens stored as bcrypt hashes
- **Shell safety**: Deny-list blocks destructive commands (rm -rf, shutdown, etc.); optional allow-list mode

## 💻 CLI Reference

| Command | Description |
|---------|-------------|
| `nanobot onboard` | Initialize config & workspace |
| `nanobot onboard --wizard` | Interactive setup wizard |
| `nanobot agent` | Interactive chat |
| `nanobot agent -m "..."` | Send a single message |
| `nanobot gateway` | Start the gateway (all channels + WebUI) |
| `nanobot webui` | Generate a WebUI login URL |
| `nanobot status` | Show status |
| `nanobot provider login <provider>` | OAuth login (openai-codex, github-copilot) |
| `nanobot channels login <channel>` | Interactive channel login (whatsapp, weixin) |
| `nanobot channels status` | Show channel status |
| `nanobot plugins list` | List channel plugins |

Interactive mode exits: `exit`, `quit`, `/exit`, `/quit`, `:q`, or `Ctrl+D`.

<details>
<summary><b>Heartbeat (Periodic Tasks)</b></summary>

The gateway checks `HEARTBEAT.md` in your workspace periodically (default 30 min). If the file has tasks, the agent executes them and delivers results to your most recently active chat channel.

Edit `~/.nanobot/workspace/HEARTBEAT.md`:

```markdown
## Periodic Tasks

- [ ] Check weather forecast and send a summary
- [ ] Scan inbox for urgent emails
```

The agent can also manage this file itself — ask it to "add a periodic task".

</details>

## 🔌 Multiple Instances

Run multiple nanobot instances with separate configs and workspaces.

```bash
# Initialize
nanobot onboard --config ~/.nanobot-telegram/config.json --workspace ~/.nanobot-telegram/workspace
nanobot onboard --config ~/.nanobot-discord/config.json --workspace ~/.nanobot-discord/workspace

# Run
nanobot gateway --config ~/.nanobot-telegram/config.json
nanobot gateway --config ~/.nanobot-discord/config.json
```

> Each instance must use a different port if running simultaneously.

## 🐳 Docker

### Docker Compose

```bash
docker compose run --rm nanobot-cli onboard   # first-time setup
vim ~/.nanobot/config.json                     # add API keys
docker compose up -d nanobot-gateway           # start gateway
```

### Docker

```bash
# Build
docker build -t nanobot .

# Initialize
docker run -v ~/.nanobot:/root/.nanobot --rm nanobot onboard

# Configure
vim ~/.nanobot/config.json

# Run gateway
docker run -v ~/.nanobot:/root/.nanobot -p 18790:18790 -p 18791:18791 nanobot gateway

# Single command
docker run -v ~/.nanobot:/root/.nanobot --rm nanobot agent -m "Hello!"
```

> Port 18790 is the gateway port, 18791 is the WebUI port.

## 🐧 Linux Service

Run the gateway as a systemd user service:

**1.** Find the binary: `which nanobot`

**2.** Create `~/.config/systemd/user/nanobot-gateway.service`:

```ini
[Unit]
Description=Nanobot Gateway
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/nanobot gateway
Restart=always
RestartSec=10
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=%h

[Install]
WantedBy=default.target
```

**3.** Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable --now nanobot-gateway
```

> Keep the service running after logout: `loginctl enable-linger $USER`

## 📁 Project Structure

```
nanobot/
├── agent/          # Core agent logic
│   ├── loop.py     #   Agent loop (LLM ↔ tool execution)
│   ├── context.py  #   Prompt builder (team + user memory injection)
│   ├── memory.py   #   Dual-layer persistent memory
│   ├── skills.py   #   Skills loader
│   ├── subagent.py #   Background task execution
│   └── tools/      #   Built-in tools (filesystem, shell, web, MCP, cron, spawn)
├── team/           # Team mode
│   ├── schema.py   #   TeamMember / TeamRegistry dataclasses
│   └── manager.py  #   Member CRUD, channel resolution, per-user paths
├── webui/          # Web admin dashboard
│   ├── app.py      #   FastAPI application factory
│   ├── auth.py     #   Token + session management
│   ├── routes/     #   Chat, Config, Skills, Team API routes
│   ├── templates/  #   HTML templates (Jinja2)
│   └── static/     #   CSS / JS assets
├── command/        # Slash command routing
│   ├── router.py   #   CommandRouter (priority / exact / prefix)
│   ├── builtin.py  #   /new, /stop, /status, /help, /restart
│   └── team.py     #   /team, /invite, /bind, /promote, /demote, /kick, /profile
├── channels/       # Chat channel integrations (13+ platforms, plugin-based)
├── bus/            # Message routing (async queues)
├── cron/           # Scheduled tasks (with per-creator ownership)
├── heartbeat/      # Proactive wake-up and periodic task execution
├── providers/      # LLM providers (20+ providers, registry-based)
├── session/        # Conversation sessions (per-user DM routing)
├── config/         # Configuration schema (Pydantic)
├── skills/         # Built-in skills (github, weather, summarize, tmux, etc.)
├── security/       # SSRF protection, URL validation
├── templates/      # Default AGENTS.md, SOUL.md, TOOLS.md, MEMORY.md
└── cli/            # Typer CLI commands
```

## 🤝 Contributing

PRs welcome! The codebase is intentionally small and readable.

### Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable releases — bug fixes and minor improvements |
| `nightly` | Experimental features — new features and breaking changes |

When in doubt, target `nightly`.

---

<p align="center">
  <em>nanobot — Ultra-lightweight AI assistant, built for teams.</em>
</p>
