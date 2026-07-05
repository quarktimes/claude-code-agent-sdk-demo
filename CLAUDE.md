# SDK Demo 项目

## 技术栈
- Python 3.11+
- Claude Agent SDK

## 项目结构
- `src/` — 待分析的示例代码
- `tests/` — 示例测试（含失败测试）
- `scripts/` — Agent SDK 脚本
- `hooks/` — Hook 示例

## 运行方式
```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/code_analyzer.py src/
python scripts/test_fixer.py
```
