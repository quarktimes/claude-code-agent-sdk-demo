#!/usr/bin/env python3
"""测试修复 Agent — 运行测试、分析失败、修复验证（两阶段工作流）"""
import asyncio, subprocess, json, sys, os
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, tool, create_sdk_mcp_server


# --- 自定义工具 ---
@tool(name="run_tests", description="运行 pytest 测试并返回结果",
      parameters={"test_path": str, "verbose": bool})
async def run_tests(args):
    test_path = args.get("test_path", "tests/")
    cmd = ["pytest", test_path, "--tb=short", "-q"]
    if args.get("verbose"): cmd.append("-v")
    cmd.extend(["--json-report", "--json-report-file=test-results.json"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            with open("test-results.json") as f: report = json.load(f)
        except: report = None
        output = {"return_code": result.returncode, "success": result.returncode == 0}
        if report:
            output["summary"] = {"total": report.get("summary",{}).get("total",0),
                                 "passed": report.get("summary",{}).get("passed",0),
                                 "failed": report.get("summary",{}).get("failed",0)}
            output["failed_tests"] = [
                {"name": t["nodeid"], "message": t.get("call",{}).get("longrepr","")}
                for t in report.get("tests",[]) if t.get("outcome")=="failed"
            ]
        return {"content": [{"type": "text", "text": json.dumps(output, indent=2)}]}
    except subprocess.TimeoutExpired:
        return {"content": [{"type": "text", "text": "超时"}], "isError": True}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"错误: {e}"}], "isError": True}

test_tools = create_sdk_mcp_server(name="test-tools", version="1.0.0", tools=[run_tests])

# --- Hooks ---
FORBIDDEN = ["setup.py", "pyproject.toml", "requirements.txt", "conftest.py"]
ALLOWED_PREFIXES = ["tests/", "src/"]

async def check_modification(input_data, tool_use_id, context):
    tool_name, inp = input_data["tool_name"], input_data["tool_input"]
    if tool_name in ["Write", "Edit"]:
        fp = inp.get("file_path", "")
        if any(f in fp for f in FORBIDDEN):
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                    "permissionDecision": "deny", "permissionDecisionReason": f"禁止修改 {fp}"}}
        if not any(fp.startswith(p) for p in ALLOWED_PREFIXES):
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                    "permissionDecision": "ask", "permissionDecisionReason": f"{fp} 不在允许目录"}}
    return {}

# --- 主程序 ---
async def main():
    options = ClaudeAgentOptions(
        model="sonnet",
        mcp_servers={"test-tools": test_tools},
        allowed_tools=["Read","Write","Edit","Grep","Glob","Bash(pytest:*)",
                       "mcp__test-tools__run_tests"],
        permission_mode="default",
        max_turns=30,
        hooks={"PreToolUse": [{"matcher": "Write|Edit", "hooks": [check_modification]}]}
    )

    print("\n🧪 测试修复 Agent 启动\n" + "="*50)

    async with ClaudeSDKClient(options=options) as client:
        # 阶段一：分析
        print("\n📊 阶段 1: 运行测试 + 分析失败原因...")
        await client.query("""运行测试套件。对每个失败的测试分析原因并提出修复方案。
注意：只分析，不要修改任何文件。分析完成后请总结失败原因。""")

        async for msg in client.receive_response():
            if msg.type == "text": print(msg.text)
            elif msg.type == "tool_use": print(f"  🔧 工具: {msg.tool_name}")

        # 确认
        confirm = input("\n✋ 确认执行修复? (y/n): ")
        if confirm.lower() != "y":
            print("已取消"); return

        # 阶段二：修复
        print("\n🔧 阶段 2: 执行修复并验证...")
        await client.update_options(permission_mode="acceptEdits")
        await client.query("执行修复方案，修复后重新运行测试验证。")

        async for msg in client.receive_response():
            if msg.type == "text": print(msg.text)
            elif msg.type == "tool_use": print(f"  🔧 {msg.tool_name}: {msg.tool_input.get('file_path','') or msg.tool_input.get('command','')}")
            elif msg.type == "result":
                print(f"\n{'='*50}")
                print(f"✅ 完成! 耗时 {msg.duration_ms/1000:.1f}s  费用 ${msg.total_cost_usd:.4f}  轮次 {msg.num_turns}")

if __name__ == "__main__":
    asyncio.run(main())
