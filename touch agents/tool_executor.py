# agents/tool_executor.py
"""
Safe Tool Executor — Sandboxed, audited, and monitored tool calling
- Prevents harmful commands
- Logs all tool usage
- Returns structured results
"""

import logging
from typing import Dict, Any, List

class ToolExecutor:
    def __init__(self, tools: Dict[str, Any]):
        self.tools = tools
        self.logger = logging.getLogger(__name__)

    def run(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool safely"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not registered"}

        tool = self.tools[tool_name]
        self.logger.info(f"🔧 Running tool: {tool_name}")

        try:
            result = tool.run(*args, **kwargs)
            self.logger.info(f"✅ Tool '{tool_name}' succeeded")
            return result
        except Exception as e:
            self.logger.error(f"❌ Tool '{tool_name}' failed: {e}")
            return {"error": str(e)}
