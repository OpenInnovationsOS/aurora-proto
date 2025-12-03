# coder/aurora_coder.py
"""
AURORA-CoderX: AI-Powered Code Generation, Testing & Patching
- Generates code from natural language
- Auto-writes Pytest unit tests
- Applies patches to files
- Executes safely in Docker sandbox
"""

import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel
from core.aurora_base import AuroraBase
from agents.tools.code_executor import CodeExecutorTool


class CodeGenerationResult(BaseModel):
    """Structured output for code generation"""
    code: str
    tests: str = ""
    patch_applied: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AuroraCoder:
    def __init__(self, llm: AuroraBase):
        self.llm = llm
        self.executor = CodeExecutorTool()

    def generate_code(
        self,
        task: str,
        language: str = "python",
        include_tests: bool = True,
        max_tokens: int = 2048
    ) -> CodeGenerationResult:
        """Generate code from natural language task"""
        prompt = f"""You are AURORA-CoderX, an expert code generator.
Task: {task}
Language: {language}

Generate ONLY the code (no explanations). If include_tests=True, also generate a Pytest file.

Example for 'add two numbers':
```python
def add(a, b):
    return a + b
