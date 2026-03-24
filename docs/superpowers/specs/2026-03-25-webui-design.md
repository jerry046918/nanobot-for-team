# nanobot WebUI 设计文档

## 概述

为 nanobot 添加一个集成到 gateway 的 Web 管理后台，仅管理员可通过 CLI 生成的临时 Token 登录。

## 技术栈

- **后端**: FastAPI + Uvicorn
- **模板**: Jinja2
- **前端交互**: HTMX + WebSocket
- **样式**: 自定义 CSS（无框架依赖）

## 核心功能模块

### 1. 认证模块

**登录流程**:
1. 运行 `nanobot webui` 命令
2. 生成随机 32 字符 Token
3. 打印带 Token 的 URL: `http://host:port/?token=xxx`
4. 浏览器打开 URL 自动登录
5. Token 默认 24 小时过期（可配置）

**Token 存储**: `{workspace}/webui_tokens.json`
- Token 使用 bcrypt 哈希存储，不存明文
- 存储格式: `{"token_hash": "...", "created_at": "...", "expires_at": "...", "last_used": "..."}`

**Session 机制**:
- 使用服务端 Session 存储（内存字典）
- Session ID 通过加密 Cookie 传递
- Token 验证成功后创建 Session，Token 哈希与 Session 绑定

**WebSocket 认证**:
- WebSocket 连接时通过查询参数传递 session cookie 或 token
- 服务端验证 Session 有效性后才允许连接

**配置项**:
| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `webui.enabled` | bool | true | 是否启用 WebUI |
| `webui.host` | str | 同 gateway | 绑定地址 |
| `webui.port` | int | gateway.port + 1 | 端口 |
| `webui.token_ttl_hours` | int | 24 | Token 有效期（小时） |

**CLI 命令**:
```bash
nanobot webui              # 生成新 Token 并打印登录 URL
nanobot webui --no-open    # 不自动打开浏览器
nanobot webui --revoke-all # 撤销所有 Token
```

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /?token=xxx | Token 登录 |
| POST | /api/auth/logout | 登出当前 Session |
| DELETE | /api/auth/tokens/{token_id} | 撤销指定 Token |

### 2. 聊天模块

**界面布局**:
- 左侧: Session 列表（可搜索、点击切换）
- 右侧: 聊天区域（Markdown 渲染、代码高亮）

**Session Key 约定**:
- WebUI 使用 `webui:admin` 作为默认 session key
- 可查看其他 channel 的会话历史（只读），session key 格式: `{channel}:{chat_id}`
- 只能从 `webui:admin` 发起对话，不能操作其他 session

**消息格式** (与 `Session.get_history()` 一致):
```json
{
  "role": "user|assistant|tool",
  "content": "...",
  "timestamp": "2026-03-25T10:00:00Z",
  "tool_calls": [...],  // optional
  "tool_call_id": "..."  // optional for tool role
}
```

**功能**:
- WebSocket 实时流式输出
- 查看所有 channel 的会话历史（只读）
- 只能从 WebUI session 发起对话
- Session 搜索过滤

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /chat | 聊天页面 |
| GET | /api/sessions | 获取 session 列表 |
| GET | /api/sessions/{key}/history | 获取会话历史 |
| WS | /ws/chat?session_id=xxx | WebSocket 聊天连接 |

### 3. 配置模块

**配置分组**:
| 分组 | 配置项 |
|------|--------|
| Agents | model, provider, temperature, max_tokens, context_window_tokens, max_tool_iterations, workspace, reasoning_effort |
| Providers | 20+ 提供商的 api_key, api_base, extra_headers |
| Channels | 各渠道的 enabled, token, allowFrom, streaming 等 |
| Tools | web.search, web.proxy, exec.enable, exec.timeout, restrict_to_workspace, mcp_servers |
| Gateway | host, port, heartbeat.enabled, heartbeat.interval_s |
| Team | enabled |
| WebUI | enabled, host, port, token_ttl_hours |

**配置验证**:
- 保存前使用 Pydantic 验证配置结构
- 验证失败返回详细错误信息: `{"error": "message", "code": "VALIDATION_ERROR", "details": [...]}`
- 保存前自动备份当前配置为 `config.json.bak`

**配置重载**:
- `POST /api/config/reload` 触发热重载
- 重载行为:
  - Channels: 禁用已删除的渠道，启用新增渠道，更新配置的渠道会重启
  - MCP Servers: 断开旧连接，建立新连接
  - Providers: 更新 API 配置（立即生效）
  - Heartbeat: 更新间隔配置

**特殊处理**:
- API Key 显示为 `••••••••`，只有修改时才显示明文
- MCP Servers 为动态列表，支持添加/删除/编辑

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /config | 配置页面 |
| GET | /api/config | 获取完整配置 |
| PUT | /api/config | 保存配置（带验证和备份） |
| POST | /api/config/validate | 仅验证配置 |
| POST | /api/config/reload | 重载配置 |

### 4. Skills 模块

**功能**:
- 列出内置和自定义 Skills
- 显示可用性状态（依赖检查）
- 编辑 SKILL.md 内容
- 配置依赖（CLI 工具、环境变量）
- 设置 `always` 加载

**导入方式**:
1. **ZIP 压缩包上传**: 需要 `unzip` 工具解压
2. **本地文件夹选择**: 浏览器选择或输入路径
3. **GitHub URL 导入**: 使用 `gh` CLI 或 GitPython 克隆

**导入安全**:
- ZIP 解压时检查路径，防止路径穿越攻击（禁止 `../` 开头的路径）
- GitHub 导入时验证 URL 格式
- 导入的文件大小限制（默认 10MB）

**导出**: 导出为 ZIP 压缩包

**版本追踪**:
- 自定义 Skills 记录导入来源和版本（commit hash for GitHub）

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /skills | Skills 页面 |
| GET | /api/skills | 获取 Skills 列表 |
| GET | /api/skills/{name} | 获取 Skill 详情 |
| POST | /api/skills | 创建/更新 Skill |
| DELETE | /api/skills/{name} | 删除 Skill |
| POST | /api/skills/import/zip | 导入 ZIP |
| POST | /api/skills/import/folder | 导入文件夹 |
| POST | /api/skills/import/github | 从 GitHub 导入 |
| GET | /api/skills/{name}/export | 导出 Skill 为 ZIP |

### 5. 团队模块

**功能**:
- 成员列表（昵称、角色、渠道绑定、加入时间、邀请人）
- 添加/移除成员
- 修改角色（admin/member）
- 渠道绑定（一个成员可绑定多个渠道 ID）

**数据结构**:
```json
{
  "nickname": "alice",
  "role": "admin",
  "channel_ids": {
    "telegram": "123456",
    "discord": "789012"
  },
  "joined_at": "2026-03-20T10:00:00Z",
  "invited_by": "system"
}
```

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /team | 团队页面 |
| GET | /api/team/members | 获取成员列表 |
| POST | /api/team/members | 添加成员 |
| PUT | /api/team/members/{nickname} | 更新成员 |
| DELETE | /api/team/members/{nickname} | 移除成员 |

## 文件结构

```
nanobot/
├── webui/
│   ├── __init__.py
│   ├── app.py              # FastAPI 应用
│   ├── auth.py             # Token 生成和验证
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py         # 认证路由
│   │   ├── chat.py         # 聊天路由
│   │   ├── config.py       # 配置路由
│   │   ├── skills.py       # Skills 路由
│   │   └── team.py         # 团队路由
│   ├── templates/
│   │   ├── base.html       # 基础模板
│   │   ├── login.html      # 登录页
│   │   ├── chat.html       # 聊天页
│   │   ├── config.html     # 配置页
│   │   ├── skills.html     # Skills 页
│   │   └── team.html       # 团队页
│   └── static/
│       ├── css/style.css
│       └── js/app.js        # HTMX + WebSocket
├── config/schema.py        # 新增 WebUIConfig
└── cli/commands.py         # 新增 webui 命令
```

## 集成方式

WebUI 作为 gateway 的内置服务启动：

```python
# 在 gateway 启动时
if config.webui.enabled:
    import uvicorn
    from nanobot.webui.app import create_app

    app = create_app(bus, agent, config, team_manager)
    config_webui = uvicorn.Config(app, host=config.webui.host, port=config.webui.port)
    # 在后台线程运行
```

## 错误处理

**标准错误响应格式**:
```json
{
  "error": "Human readable message",
  "code": "ERROR_CODE",
  "details": [{"field": "xxx", "message": "..."}]
}
```

**错误代码**:
| 代码 | 说明 |
|------|------|
| UNAUTHORIZED | 未认证 |
| TOKEN_EXPIRED | Token 已过期 |
| VALIDATION_ERROR | 配置验证失败 |
| NOT_FOUND | 资源不存在 |
| IMPORT_FAILED | 导入失败 |
| RATE_LIMITED | 请求过于频繁 |

## 审计日志

所有管理操作记录到 `{workspace}/audit.log`:
- 配置变更
- 成员添加/移除/角色变更
- Skill 导入/删除
- Token 生成/撤销

日志格式: `[timestamp] [action] [actor] [details]`

## 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/health | WebUI 服务状态 |

响应:
```json
{
  "status": "healthy",
  "gateway_connected": true,
  "active_sessions": 3
}
```

## 安全考虑

1. Token 使用 bcrypt 哈希存储
2. Session 通过加密 Cookie 管理
3. WebSocket 需要有效 Session 认证
4. ZIP 导入时防止路径穿越攻击
5. Token 过期自动清理
6. 操作审计日志
7. 配置变更前自动备份

## 配置 Schema 更新

```python
class WebUIConfig(Base):
    """WebUI configuration."""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 18791  # gateway.port + 1
    token_ttl_hours: int = 24

class Config(BaseSettings):
    # ... existing fields ...
    webui: WebUIConfig = Field(default_factory=WebUIConfig)
```
