#!/usr/bin/env python3
"""代码分析 Agent — 扫描代码库、识别问题、生成报告"""
import asyncio, sys, os
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


async def analyze_codebase(directory: str) -> dict:
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob"],
        permission_mode="plan",
        max_turns=25,
        cwd=directory,
        model="sonnet"
    )

    result = {"directory": directory, "timestamp": datetime.now().isoformat(),
              "report": [], "metadata": {}}

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(f"""分析代码库 {directory}：
1. 识别项目结构和技术栈
2. 检查代码质量（命名、组织、重复）
3. 查找安全隐患、Bug、性能问题（注明文件和行号）
4. 提出改进建议（按优先级排序）
输出 Markdown 格式。""")

            async for msg in client.receive_response():
                match msg.type:
                    case "text": result["report"].append(msg.text); print(msg.text)
                    case "tool_use":
                        info = msg.tool_input.get('file_path', msg.tool_input.get('pattern', ''))
                        print(f"  🔍 {msg.tool_name}: {info}")
                    case "result":
                        result["metadata"] = {
                            "duration_ms": msg.duration_ms,
                            "total_cost_usd": msg.total_cost_usd,
                            "num_turns": msg.num_turns,
                        }
                    case "error": print(f"  ❌ {msg.error}")
    except Exception as e: result["error"] = str(e)
    return result


async def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/code_analyzer.py <目录>")
        sys.exit(1)
    directory = sys.argv[1]
    print(f"\n🔍 开始分析: {directory}\n{'='*50}")
    result = await analyze_codebase(directory)
    m = result.get("metadata", {})
    print(f"\n{'='*50}")
    print(f"✅ 分析完成")
    if m: print(f"   耗时: {m.get('duration_ms',0)/1000:.1f}s  费用: ${m.get('total_cost_usd',0):.4f}  轮次: {m.get('num_turns',0)}")
    fname = f"analysis-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    with open(fname, "w") as f: f.write("\n".join(result.get("report", [])))
    print(f"   报告: {fname}")


if __name__ == "__main__":
    asyncio.run(main())
