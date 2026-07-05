# Claude Code Agent SDK Demo

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Claude Agent SDK](https://img.shields.io/badge/Claude_Agent_SDK-0.2.110-purple.svg)]()

**通过可运行的示例项目，体验 Claude Agent SDK 的编程式 Agent 控制能力。**

---

## ✨ 项目简介

本项目包含两个完整的 Agent SDK 示例，展示从基础到进阶的 Agent 编程模式：

| 项目 | 技术要点 | 难度 |
|------|---------|------|
| [🔍 代码分析 Agent](#-项目一代码分析-agent) | 只读分析、工具白名单、权限控制、流式响应 | ⭐ 入门 |
| [🔧 测试修复 Agent](#-项目二测试修复-agent) | 自定义 MCP 工具、PreToolUse Hooks、两阶段工作流、动态权限切换 | ⭐⭐ 进阶 |

---

## 🚀 快速开始

### 前置条件

1. **Anthropic API Key** — [console.anthropic.com](https://console.anthropic.com) 获取
2. **Python 3.11+**

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

---

## 📦 项目一：代码分析 Agent

扫描代码目录，识别项目结构、发现安全隐患和代码质量问题，生成 Markdown 报告。

### 运行

```bash
python scripts/code_analyzer.py src/
```

### 示例输出

```
🔍 开始分析: src/
==================================================
  🔍 Glob: **/*
  🔍 Read: src/auth.ts
  🔍 Read: src/data.ts
  🔍 Grep: TODO

## 潜在问题
1. **安全隐患** (src/auth.ts:5-7) — SQL 查询使用字符串拼接，存在注入风险
2. **性能问题** (src/data.ts:7-12) — 循环内多次查询数据库（N+1 问题）

==================================================
✅ 分析完成
   耗时: 15.3s  费用: $0.0523  轮次: 8
   报告: analysis-report-20250118-103045.md
```

### 核心设计

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"],  # 只读工具
    permission_mode="plan",                    # 系统级强制只读
    max_turns=25,                              # 防失控
    model="sonnet"                             # 平衡性能与成本
)
```

---

## 🔧 项目二：测试修复 Agent

两阶段工作流：自动运行测试 → 分析失败原因 → 人工确认 → 执行修复 → 重新验证。

### 先查看测试状态

```bash
# 可以看到 2 个测试失败（故意埋的）
python -m pytest tests/ -v
```

### 运行

```bash
python scripts/test_fixer.py
```

### 示例交互

```
🧪 测试修复 Agent 启动
==================================================

📊 阶段 1: 运行测试 + 分析失败原因...
  🔧 工具: mcp__test-tools__run_tests

Test Results: 总 4, 通过 2, 失败 2

失败分析:
1. tests/test_api.py::test_get_user_endpoint
   → 接口路径从 /api/user 改为 /api/users
   → 修复: 更新测试中的 URL 断言

2. tests/test_user.py::test_user_creation
   → 用户默认状态从 'active' 改为 'pending'
   → 修复: 更新测试断言值

✋ 确认执行修复? (y/n): y

🔧 阶段 2: 执行修复并验证...
  🔧 Edit: tests/test_api.py
  🔧 Edit: tests/test_user.py
  🔧 mcp__test-tools__run_tests

✅ 全部通过! (4/4)
==================================================
✅ 完成! 耗时 45.3s  费用 $0.0821  轮次 12
```

### 进阶特性

| 特性 | 实现方式 |
|------|---------|
| **自定义工具** | `@tool` 装饰器 + MCP Server |
| **安全 Hooks** | PreToolUse 拦截文件修改 |
| **两阶段工作流** | `permission_mode` 从 `default` 动态切换为 `acceptEdits` |
| **人工确认** | `input()` 阻塞等待，Human-in-the-loop |
| **审计日志** | PostToolUse Hook 记录所有修改 |

---

## 🧠 关键概念速查

| 概念 | 说明 | 对应代码 |
|------|------|---------|
| `ClaudeAgentOptions` | Agent 配置对象 | `options = ClaudeAgentOptions(...)` |
| `allowed_tools` | 工具白名单 | `["Read", "Grep", "Glob"]` |
| `permission_mode` | 权限模式 | `"plan"`(只读) / `"default"` / `"acceptEdits"` |
| `max_turns` | 最大 Agentic Loop 轮次 | `max_turns=25` |
| `@tool` | 自定义工具装饰器 | `@tool(name="run_tests", ...)` |
| `create_sdk_mcp_server` | 工具注册为 MCP | `create_sdk_mcp_server(tools=[...])` |
| PreToolUse Hook | 工具执行前拦截 | `"permissionDecision": "deny"` |
| `client.update_options()` | 运行时动态改配置 | `await client.update_options(permission_mode="acceptEdits")` |

---

## 📁 项目结构

```
claude-code-agent-sdk-demo/
├── CLAUDE.md                    # 项目规范（AI 辅助开发用）
├── README.md
├── .env.example                 # 环境变量模板
├── src/                         # 待分析的示例代码
│   ├── index.ts                 #   入口
│   ├── auth.ts                  #   SQL 注入漏洞（故意埋的）
│   ├── data.ts                  #   N+1 查询问题（故意埋的）
│   └── utils/helpers.ts
├── tests/                       # 示例测试
│   ├── test_user.py             #   ❌ 默认值变更导致失败
│   ├── test_api.py              #   ❌ 接口路径变更导致失败
│   └── conftest.py
├── scripts/                     # Agent SDK 脚本
│   ├── code_analyzer.py         #   🔍 代码分析 Agent
│   └── test_fixer.py            #   🔧 测试修复 Agent
└── hooks/
    └── pre-push-check.sh        #   🪝 PreToolUse Hook 示例
```

---

## 📚 参考

- [Claude Agent SDK 文档](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)
- [专栏：Claude Code 工程化实战](https://time.geekbang.org/column/intro/101113501)

---

## 📄 许可证

MIT
