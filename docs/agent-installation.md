# Agent Skill Installation

`skills/krita-finegrained-anime` 是唯一的 canonical skill。运行 `python scripts/sync_agent_layouts.py` 会生成并覆盖仓库内的 Agent 专用镜像；CI 使用 `--check` 阻止镜像漂移。

## 支持的目录

| Agent | 项目级 | 用户级 |
| --- | --- | --- |
| Codex | `.agents/skills/<name>` | `~/.agents/skills/<name>` |
| OpenCode | `.opencode/skills/<name>` | `~/.config/opencode/skills/<name>` |
| Claude Code | `.claude/skills/<name>` | `~/.claude/skills/<name>` |
| WorkBuddy | `skills/<name>` | `~/.workbuddy/skills/<name>` |

Codex、OpenCode 和 Claude Code 的路径遵循其官方 skill 文档。WorkBuddy 项目级布局遵循其公开 skill 仓库的 `skills/<name>/SKILL.md` 约定；不同 WorkBuddy 版本如未自动扫描用户级目录，可直接导入 `skills/krita-finegrained-anime`。

## 安装方式

跨平台 Python 安装器：

```bash
python scripts/install_agent_skill.py --agent codex --scope user
python scripts/install_agent_skill.py --agent all --scope project --project-root /path/to/project
```

Windows PowerShell 包装器：

```powershell
.\scripts\install_agent_skill.ps1 -Agent claude -Scope user
```

目标已存在时安装器会停止。确认需要覆盖后增加 `--force`，PowerShell 中使用 `-Force`。

## 运行依赖

Skill 是 Agent 的操作说明，不包含完整 Python 包和 Krita 插件。要实际控制 Krita，还需：

1. 在本仓库运行 `pip install -e .`，使 `krita-anime` 可调用。
2. 运行 `scripts/install_plugin.ps1 -InstallToKrita` 安装插件。
3. 在 Krita 中启用 `Krita MCP Bridge` 并重启 Krita。
4. 用 `krita health` 或 `scripts/smoke_krita.py --health-only` 检查连接。

仅需审阅或生成 `AnimePlan` 时可以不启动 Krita；执行笔刷、矢量图层和分镜动作时必须连接 Krita。
