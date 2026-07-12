# Krita Anime Skill

基于 [`edithatogo/krita-cli`](https://github.com/edithatogo/krita-cli) 定制的 Krita 动漫绘制 CLI、HTTP 插件、MCP 服务和跨 Agent skill。

项目面向可编辑的精细化动漫生产，而不是只输出一张扁平图片。它把严格的 `AnimePlan` JSON 编译为受约束的 Krita 动作，支持原生笔刷引擎、压感笔划、线条稳定器、贝塞尔路径、SVG 矢量图层、分镜和角色一致性包。

## 主要能力

- 创建分层 `.kra` 动漫插画和故事板，并导出 PNG/JPG 预览。
- 使用 Krita 原生笔刷预设、压感笔划和稳定器完成线稿与上色。
- 使用贝塞尔路径和 SVG 矢量图层制作可编辑线条、形状和标注。
- 通过 character pack 固定脸型、眼睛、发型轮廓、比例、色板和标志物，再改变动作、表情、服装、镜头与场景。
- 让 DeepSeek 等纯文本模型只负责生成严格 JSON，本地 schema、编译器和 Krita 插件负责验证与执行。
- 同时提供 CLI、MCP 和 Agent Skill 三种调用面。

纯文本模型不能直接理解参考图。要复刻给定人物，先由视觉模型或人工把参考图转换成 character pack；此后 DeepSeek 等单模态模型可以基于该结构化身份描述生成新动作、服装和场景。

## 架构

```text
Agent / DeepSeek
      |
      v
AnimePlan JSON -> validator/compiler -> bounded Krita actions
                                          |
                                          v
CLI or MCP -> localhost HTTP bridge -> Krita Python plugin
                                          |
                                          v
                    paint/vector/storyboard layers in .kra
```

## 本地安装

要求 Python 3.10+ 和 Krita 5/6。开发依赖和下载都可以留在当前非系统盘工作区：

```powershell
git clone https://github.com/xxxyyyzzz3984/krita-anime-skill.git
cd krita-anime-skill
python -m venv .venv
$env:HTTP_PROXY='http://127.0.0.1:10080'
$env:HTTPS_PROXY='http://127.0.0.1:10080'
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

把插件暂存到仓库内，不写入系统盘：

```powershell
.\scripts\install_plugin.ps1
```

需要 Krita 实际加载时，执行下面的命令，并在 Krita 的 Python Plugin Manager 中启用 `Krita MCP Bridge`：

```powershell
.\scripts\install_plugin.ps1 -InstallToKrita
```

重启 Krita 后检查桥接服务：

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe scripts\smoke_krita.py --health-only
```

## Agent Skill 安装

canonical skill 位于 [`skills/krita-finegrained-anime`](skills/krita-finegrained-anime)。仓库同时提交以下兼容布局：

| Agent | 项目级目录 |
| --- | --- |
| Codex | `.agents/skills/krita-finegrained-anime` |
| OpenCode | `.opencode/skills/krita-finegrained-anime` |
| Claude Code | `.claude/skills/krita-finegrained-anime` |
| WorkBuddy | `skills/krita-finegrained-anime` |

从本地 clone 安装到用户目录：

```powershell
.\scripts\install_agent_skill.ps1 -Agent codex -Scope user
.\scripts\install_agent_skill.ps1 -Agent opencode -Scope user
.\scripts\install_agent_skill.ps1 -Agent claude -Scope user
.\scripts\install_agent_skill.ps1 -Agent workbuddy -Scope user
```

也可一次安装全部，或安装到另一个项目：

```powershell
.\scripts\install_agent_skill.ps1 -Agent all -Scope user
.\scripts\install_agent_skill.ps1 -Agent codex -Scope project -ProjectRoot D:\work\my-project
```

Codex 还可以直接使用内置 `$skill-installer` 从本 GitHub 仓库安装。安装完成后重启对应 Agent，使其重新发现 skill。详细路径和兼容性说明见 [`docs/agent-installation.md`](docs/agent-installation.md)。

## 使用

创建 character pack：

```powershell
.\.venv\Scripts\python.exe -m krita_anime.cli character init outputs\hero.json --id hero
```

使用 DeepSeek 生成严格计划。密钥按顺序读取 `DEEPSEEK_API_KEY`、`ds-api-key.txt`、`ds-ap-key.txt`，这些文件均被 Git 忽略：

```powershell
.\.venv\Scripts\python.exe -m krita_anime.cli plan `
  "角色穿雨衣在车站奔跑，四分之三视角，保持人物一致性" `
  --character outputs\hero.json `
  --output outputs\rainy-station.json
```

验证、编译和执行：

```powershell
.\.venv\Scripts\python.exe -m krita_anime.cli validate outputs\rainy-station.json
.\.venv\Scripts\python.exe -m krita_anime.cli compile outputs\rainy-station.json -o outputs\rainy-station.commands.json
.\.venv\Scripts\python.exe -m krita_anime.cli run outputs\rainy-station.json --report outputs\rainy-station.report.json
```

分镜 dry run：

```powershell
.\.venv\Scripts\python.exe -m krita_anime.cli run examples\storyboard.json --dry-run
```

在支持 Skills 的 Agent 中调用 `$krita-finegrained-anime`，并描述角色、动作、服装、镜头、场景和交付格式。Agent 会先建立/读取 character pack，再生成计划、执行 Krita 动作并检查分层结果。

## 开发与验证

```powershell
.\.venv\Scripts\python.exe scripts\sync_agent_layouts.py --check
.\.venv\Scripts\python.exe -m pytest tests\anime tests\unit tests\integration tests\property tests\packaging tests\e2e\test_e2e_mock.py tests\test_phase_11.py -o addopts='' -q
.\.venv\Scripts\python.exe -m build
```

Krita 5 的 PyQt5 和 Krita 6 的 PyQt6 通过兼容层支持。离线测试覆盖 schema、编译器、DeepSeek 适配器、HTTP 载荷、MCP 和插件纯助手逻辑；真实原生笔刷事件仍需要正在运行、画布可交互的 Krita 实例。

## 来源与许可

上游固定提交和派生说明见 [`UPSTREAM.md`](UPSTREAM.md)。本项目使用 MIT License。
