from typing import List, Dict, Any
import json

class ExecutiveAgent:
    def __init__(self, llm, tools: List, memory, max_iterations: int = 5):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.memory = memory
        self.max_iterations = max_iterations

    def plan(self, goal: str) -> List[str]:
        prompt = f"""You are AURORA Executive Agent. Break this goal into 3-5 executable steps.
Goal: {goal}
Respond ONLY as JSON: {{"steps": ["step1", "step2", ...]}}"""
        response = self.llm.generate(prompt)
        try:
            return json.loads(response)["steps"]
        except:
            # Fallback: split by newline
            return [s.strip() for s in response.split("\n") if s.strip()]

    def self_audit(self, goal: str, code: str, output: str) -> str:
        prompt = f"""[SELF-AUDIT]
Goal: {goal}
Generated Code: {code[:500]}...
Output: {output[:300]}...
Check: 1) Correct? 2) Safe? 3) Complete?
Respond in 3 bullet points."""
        return self.llm.generate(prompt, temperature=0.1)
