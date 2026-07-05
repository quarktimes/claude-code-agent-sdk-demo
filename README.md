# Claude Code Agent SDK Demo

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Claude Agent SDK](https://img.shields.io/badge/Claude_Agent_SDK-0.2.110-purple.svg)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

> **通过可运行的示例项目，零距离体验 Claude Agent SDK 的编程式 Agent 控制能力。**

---

## 📖 目录

- [项目简介](#-项目简介)
- [快速开始](#-快速开始)
- [项目一：代码分析 Agent](#-项目一代码分析-agent)
- [项目二：测试修复 Agent](#-项目二测试修复-agent)
- [示例代码说明](#-示例代码说明)
- [SDK 核心能力详解](#-sdk-核心能力详解)
- [从 CLI 到 SDK 的思维转换](#-从-cli-到-sdk-的思维转换)
- [常见问题](#-常见问题)
- [参考](#-参考)

---

## ✨ 项目简介

本项目通过两个精心设计的示例，展示 Claude Agent SDK 的完整能力图谱：

### 🔍 项目一：代码分析 Agent

让 Agent 以**只读模式**扫描代码目录，自动发现项目结构、技术栈、安全隐患和代码质量问题，最终生成结构化的 Markdown 分析报告。

**你将学到：**
- 如何用 `ClaudeAgentOptions` 配置 Agent 的边界（工具、权限、模型）
- `permission_mode="plan"` 实现系统级强制只读的原理
- 如何通过流式消息实时监控 Agent 的每一步操作
- Agentic Loop 中工具选择与结果回注的完整流程

### 🔧 项目二：测试修复 Agent

两阶段工作流——Agent 先以只读模式分析失败的测试，提出修复方案，等你确认后再获得修改权限执行修复，最后重新验证。

**你将学到：**
- 用 `@tool` 装饰器为 Agent 注入自定义能力
- 用 PreToolUse Hook 实现文件修改的安全边界
- `client.update_options()` 运行时动态切换权限模式
- 两阶段工作流：分析 → 确认 → 执行（Human-in-the-loop）

### 适用人群

| 角色 | 价值点 |
|------|--------|
| Python 开发者 | 学会用 SDK 将 Agent 嵌入自有系统 |
| AI 应用工程师 | 掌握自定义工具、Hook、权限管理等工程范式 |
| Claude Code CLI 用户 | 理解 CLI 背后 SDK 的工作原理，从使用者进阶为驾驭者 |
| 技术管理者 | 评估 Agent SDK 在生产环境中的集成可行性 |

---

## 🚀 快速开始

### 前置条件

| 条件 | 说明 |
|------|------|
| Anthropic API Key | 从 [console.anthropic.com](https://console.anthropic.com) 获取 |
| Python | 3.11+（推荐 3.11~3.12） |
| 依赖 | `claude-agent-sdk` >= 0.2.110 |

### 安装

```bash
# 克隆项目
git clone https://github.com/quarktimes/claude-code-agent-sdk-demo.git
cd claude-code-agent-sdk-demo

# 安装依赖
pip install claude-agent-sdk

# 设置 API Key
export ANTHROPIC_API_KEY=sk-ant-...
```

> **国内用户**：如无法直连 Anthropic API，可设置中转端点：
> ```bash
> export ANTHROPIC_BASE_URL=https://your-relay-service.com/v1
> ```

---

## 📦 项目一：代码分析 Agent

### 功能概述

Agent 接收一个目录路径作为参数，自动完成以下任务：

1. **项目结构识别** — 扫描目录树，识别项目类型和技术栈
2. **代码质量评估** — 检查命名规范、代码组织、重复代码
3. **安全审计** — 查找 SQL 注入、密钥泄露、XSS 等常见漏洞
4. **性能分析** — 发现 N+1 查询、循环内 IO 等性能问题
5. **报告生成** — 输出 Markdown 格式的分析报告（同时打印到终端和保存到文件）

### 运行方式

```bash
# 分析整个 src/ 目录
python scripts/code_analyzer.py src/

# 分析特定子目录
python scripts/code_analyzer.py src/utils/
```

### 执行流程拆解

当你运行 `python scripts/code_analyzer.py src/` 时：

```
你                                    Agent SDK                               Claude API
 │                                      │                                        │
 ├─ 配置 ClaudeAgentOptions ──────────→ │                                        │
 │   (只读工具 + plan 模式)             │                                        │
 │                                      │                                        │
 ├─ client.query("分析代码库...") ────→ │                                        │
 │                                      ├── 启动 Agentic Loop ────────────────→ │
 │                                      │                                        │
 │                                      │    ←── 推理：需要看项目结构 ─────────── │
 │                                      │    ←── 调用 Glob("**/*") ──────────── │
 │  ←── msg(type="tool_use") ───────── │                                        │
 │  打印 "🔍 Glob: **/*"               │                                        │
 │                                      │    ←── 推理：看看入口文件 ──────────── │
 │                                      │    ←── 调用 Read("src/index.ts") ──── │
 │  ←── msg(type="tool_use") ───────── │                                        │
 │  打印 "🔍 Read: src/index.ts"       │                                        │
 │                                      │    ←── 推理：发现 SQL 拼接 ─────────── │
 │                                      │    ←── 继续搜索 src/auth.ts ───────── │
 │  ...                                 │    ...                                 │
 │                                      │    ←── 推理完成，生成报告 ──────────── │
 │  ←── msg(type="text") ──────────── │                                        │
 │  打印分析结果                        │                                        │
 │                                      │                                        │
 │  ←── msg(type="result") ────────── │                                        │
 │  显示: 耗时/费用/轮次                │                                        │
 │                                      │                                        │
 ├─ 保存报告到 .md 文件                 │                                        │
```

### 你能从中学到

| 知识点 | 对应代码 | 为什么重要 |
|--------|---------|-----------|
| `allowed_tools` 白名单 | `["Read", "Grep", "Glob"]` | 不给 Write/Edit = 物理上无法修改代码 |
| `permission_mode="plan"` | 引擎层强制只读 | 即使 prompt 被注入恶意指令也无法执行 |
| `max_turns=25` | 限制 Agentic Loop 轮次 | 防止 Agent 跑飞，控制成本 |
| 流式消息处理 | `match msg.type:` | 实时监控 Agent 行为，是生产环境必备能力 |
| `cwd` 设置 | 指定工作目录 | Agent 的文件操作基于此路径 |

---

## 🔧 项目二：测试修复 Agent

### 功能概述

模拟真实 CI 场景——测试套件中有测试因代码变更而失败，Agent 自动完成：

1. **运行测试套件** — 调用自定义 `run_tests` 工具执行 pytest
2. **分析失败原因** — 读取失败测试的错误信息，结合源代码进行根因分析
3. **提出修复方案** — 对每个失败测试给出具体的修复建议
4. **等待人工确认** — 用户审查方案后决定是否执行
5. **执行修复** — 获得权限后修改测试代码
6. **重新验证** — 再次运行测试确认全部通过

### 先了解测试状态

项目 `tests/` 目录中有 4 个测试，其中 2 个故意失败：

```bash
python -m pytest tests/ -v --tb=short
```

你会看到：

```
tests/test_api.py::test_get_user_endpoint FAILED    # 接口路径变了
tests/test_api.py::test_create_user       PASSED
tests/test_user.py::test_user_creation    FAILED    # 默认值变了
tests/test_user.py::test_user_deletion    PASSED
```

### 运行方式

```bash
python scripts/test_fixer.py
```

### 两阶段工作流拆解

```
┌─────────────── 阶段一：分析（只读） ───────────────┐
│                                                       │
│  permission_mode="default"                             │
│  Prompt: "只分析，不要修改任何文件"                      │
│                                                       │
│  ┌────────────────────────────────┐                    │
│  │ Agentic Loop                   │                    │
│  │  ① run_tests → 发现 2 个失败   │                    │
│  │  ② Read 源代码 → 分析根因      │                    │
│  │  ③ Read 测试代码 → 定位问题行   │                    │
│  │  ④ 输出修复方案                │                    │
│  └────────────────────────────────┘                    │
│                                                       │
│  ↓ 等待人工确认 (input)                                │
└───────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  确认执行修复?     │
                    │  (y/n)            │
                    └─────────┬─────────┘
                              │ y
┌─────────────── 阶段二：执行（可写） ───────────────┐
│                                                       │
│  client.update_options(permission_mode="acceptEdits")  │
│  Prompt: "执行修复后重新运行测试验证"                    │
│                                                       │
│  ┌────────────────────────────────┐                    │
│  │ Agentic Loop                   │                    │
│  │  ① Edit tests/test_api.py      │ ← Hook 检查通过   │
│  │  ② Edit tests/test_user.py     │ ← Hook 检查通过   │
│  │  ③ run_tests → 全部通过 ✅     │                    │
│  └────────────────────────────────┘                    │
│                                                       │
│  ↓ 输出完成报告（耗时/费用/轮次）                        │
└───────────────────────────────────────────────────────┘
```

### 安全机制详解

测试修复 Agent 需要修改代码，因此比代码分析 Agent 多了两道安全防线：

**第一关：工具白名单限制**

```python
allowed_tools=["Read", "Write", "Edit", "Grep", "Glob",
               "Bash(pytest:*)",
               "mcp__test-tools__run_tests"]
```

`Bash(pytest:*)` 这种带通配符的语法，意思是"Bash 命令只能执行以 pytest 开头的命令"。

**第二关：PreToolUse Hook 拦截**

```python
FORBIDDEN = ["setup.py", "pyproject.toml", ...]     # 黑名单 → 硬拒绝
ALLOWED_PREFIXES = ["tests/", "src/"]                 # 白名单 → 允许

# 不在白名单也不在黑名单 → 弹窗问用户
```

Agent 尝试修改文件时会触发 Hook 的三种决策：
- 命中黑名单 → **deny**（硬拦截）
- 命中白名单 → **放行**
- 两者都不在 → **ask**（弹窗询问用户）

---

## 📂 示例代码说明

项目自带的示例代码和测试中有意埋入了缺陷，让 Agent 有"用武之地"。

### src/ — 待分析的代码

| 文件 | 埋入的问题 | 类型 |
|------|-----------|------|
| `src/auth.ts:5-7` | SQL 查询使用 `${email}` 字符串拼接 | 🔴 安全漏洞 |
| `src/data.ts:7-12` | 循环内逐个查询数据库（N+1） | 🟡 性能问题 |

### tests/ — 含失败测试的套件

**test_user.py** — 模拟"业务代码默认值变更导致测试失败"

```python
# 业务代码新版本：默认状态从 'active' 改为 'pending'
def get_new_user(name):
    return {"name": name, "status": "pending"}

# 测试代码未更新（仍断言 'active'）
assert user["status"] == "active"  # ❌ AssertionError
```

**test_api.py** — 模拟"接口路径变更导致测试失败"

```python
# 业务代码新版本：接口路径从 /api/user 改为 /api/users
response = {"url": "/api/users"}

# 测试代码未更新
assert response["url"] == "/api/user"  # ❌ AssertionError
```

---

## 🧠 SDK 核心能力详解

### 1. ClaudeAgentOptions — Agent 配置中心

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"],     # 工具白名单
    permission_mode="plan",                       # 权限模式
    max_turns=25,                                 # 最大循环轮次
    model="sonnet",                               # 模型选择
    cwd="/path/to/project",                       # 工作目录
    mcp_servers={...},                            # 自定义 MCP 工具
    hooks={...},                                  # Hook 配置
)
```

### 2. permission_mode 的五种模式

| 模式 | 效果 | 适用场景 |
|------|------|---------|
| `"default"` | 按 settings.json 权限规则执行 | 日常分析 |
| `"plan"` | **系统级强制只读** | 安全审计 |
| `"acceptEdits"` | 自动接受所有修改请求 | 自动化修复 |
| `"bypass"` | 跳过所有权限确认 | 完全信任场景 |
| `"none"` | 拒绝所有工具调用 | 纯对话 |

### 3. @tool 自定义工具协议

```python
@tool(
    name="工具名",                    # Agent 通过此名称调用
    description="做什么用的",          # ★ 最重要的字段
    parameters={"参数名": 类型}        # 参数规范
)
async def my_tool(args):
    # 执行业务逻辑 → MCP 标准格式返回
    return {"content": [{"type": "text", "text": json.dumps(result)}]}
```

### 4. Hooks 安全围栏

| Hook 类型 | 触发时机 | 能力 |
|-----------|---------|------|
| **PreToolUse** | 工具执行前 | 拦截/修改工具调用 |
| **PostToolUse** | 工具执行后 | 观察结果、记录日志 |
| **Stop** | 任务结束时 | 质量门控 |

---

## 🔄 从 CLI 到 SDK 的思维转换

| 维度 | Claude Code CLI | Agent SDK |
|------|----------------|-----------|
| **交互方式** | 对话式 | 编程式 |
| **控制粒度** | 粗（只控制 prompt） | 细（工具、权限、Hook 全可控） |
| **自定义工具** | 不支持 | `@tool` 装饰器注入 |
| **权限动态切换** | 不支持 | `client.update_options()` |
| **集成能力** | 仅终端 | 可嵌入 Web 服务、CI/CD |
| **适用场景** | 日常编码 | 自动化系统、产品嵌入 |

**一句话总结：** CLI 是"与 Agent 对话"，SDK 是"用代码控制 Agent"。

---

## ❓ 常见问题

<details>
<summary><strong>Q: 为什么测试修复 Agent 第一阶段不用 permission_mode="plan"？</strong></summary>

plan 模式会拒绝所有 Bash 命令（包括读取测试结果文件）。default 模式允许读取操作，配合 prompt 约束更灵活。
</details>

<details>
<summary><strong>Q: 为什么 Bash 工具要写成 Bash(pytest:*) 而不是直接用 Bash？</strong></summary>

这是**命令过滤语法**，只允许执行 pytest 开头的命令。最小权限原则——不给 Agent 执行任意命令的能力。
</details>

<details>
<summary><strong>Q: 代码分析 Agent 的 plan 模式和只用工具白名单有什么区别？</strong></summary>

工具白名单只限制工具有哪些，不限制 Bash。plan 在权限引擎层强制只读，是额外的安全层。
</details>

---

## 📁 项目结构

```
claude-code-agent-sdk-demo/
├── README.md                       # 本文档
├── CLAUDE.md                       # 项目规范
├── .env.example                    # 环境变量模板
├── src/                            # 待分析的示例代码（含故意埋入的问题）
│   ├── index.ts
│   ├── auth.ts                     # SQL 注入漏洞 🔴
│   ├── data.ts                     # N+1 性能问题 🟡
│   └── utils/helpers.ts
├── tests/                          # 示例测试套件
│   ├── test_user.py                # 默认值变更导致失败 ❌
│   ├── test_api.py                 # 接口路径变更导致失败 ❌
│   └── conftest.py
├── scripts/                        # Agent SDK 可执行脚本
│   ├── code_analyzer.py            # 代码分析 Agent
│   └── test_fixer.py               # 测试修复 Agent
└── hooks/
    └── pre-push-check.sh           # PreToolUse Hook 示例
```

---

## 📚 参考

| 资源 | 链接 |
|------|------|
| Claude Agent SDK 文档 | https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk |
| Anthropic Console | https://console.anthropic.com |

---

## 📄 许可证

MIT
