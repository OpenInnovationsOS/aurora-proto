# agents/executive_agent.py
"""
AURORA Executive Agent — Self-Monitoring, Goal-Decomposing, Tool-Calling AI
- Plans multi-step tasks
- Self-audits confidence & safety
- Routes to tools or LLM for execution
- Maintains persistent memory context
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from core.aurora_base import AuroraBase
from core.aurora_memvault import AuroraMemVault
from agents.tool_executor import ToolExecutor


class PlanStep(BaseModel):
    """Single step in an executive plan"""
    number: int
    description: str
    required_tools: List[str] = Field(default_factory=list)
    expected_output: str


class ExecutiveAgent:
    def __init__(
        self,
        llm: AuroraBase,
        tools: List,
        memory: AuroraMemVault,
        max_iterations: int = 5,
        temperature: float = 0.1
    ):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.memory = memory
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def plan(self, goal: str) -> List[PlanStep]:
        """Break goal into executable steps using LLM"""
        prompt = f"""You are AURORA Executive Agent. Break this goal into 3-7 atomic, executable steps.
Goal: {goal}

Respond ONLY as JSON array of objects with keys: "number", "description", "required_tools" (list), "expected_output".

Example:
[
  {{
    "number": 1,
    "description": "Fetch weather data for London",
    "required_tools": ["web_browse"],
    "expected_output": "JSON weather data"
  }}
]
"""
        try:
            response = self.llm.generate(prompt, temperature=self.temperature)
            steps = json.loads(response)
            return [PlanStep(**step) for step in steps]
        except Exception as e:
            self.logger.error(f"Planning failed: {e}")
            # Fallback: simple linear plan
            return [
                PlanStep(number=1, description=goal, required_tools=[], expected_output="Completion")
            ]

    def execute_step(self, step: PlanStep, context: str = "") -> Dict[str, Any]:
        """Execute one step — call tools or LLM if needed"""
        self.logger.info(f"🚀 Executing Step {step.number}: {step.description}")

        # If no tools required, use LLM to generate output
        if not step.required_tools:
            prompt = f"""You are executing Step {step.number} of a plan.
Goal: {step.description}
Context: {context}

Generate the output as requested. Be concise and factual."""
            result = self.llm.generate(prompt, max_tokens=1024)
            return {"success": True, "output": result, "tool_used": None}

        # Otherwise, route to tools
        tool_results = {}
        for tool_name in step.required_tools:
            if tool_name not in self.tools:
                tool_results[tool_name] = {"error": f"Tool '{tool_name}' not found"}
                continue

            tool = self.tools[tool_name]
            try:
                # Pass context + step description to tool
                result = tool.run(step.description, context=context)
                tool_results[tool_name] = result
            except Exception as e:
                tool_results[tool_name] = {"error": str(e)}

        return {"success": True, "output": tool_results, "tool_used": list(step.required_tools)}

    def self_audit(self, goal: str, steps: List[PlanStep], final_output: str) -> str:
        """Self-critique: Did we achieve the goal? Is it safe? Complete?"""
        prompt = f"""[SELF-AUDIT REPORT]
Goal: {goal}
Steps Taken: {[s.description for s in steps]}
Final Output: {final_output[:500]}...

Check:
1. Was the goal achieved? (Yes/No + why)
2. Were any unsafe actions taken? (Yes/No + why)
3. Is the output complete? (Yes/No + what's missing)

Respond in 3 bullet points."""
        return self.llm.generate(prompt, temperature=0.0)

    def run(self, goal: str) -> Dict[str, Any]:
        """Main entry point — execute full plan with self-monitoring"""
        self.logger.info(f"🎯 EXECUTIVE AGENT STARTED: {goal}")

        # Step 1: Plan
        steps = self.plan(goal)
        self.logger.info(f"📋 Generated {len(steps)} steps")

        # Step 2: Execute each step
        context = ""
        all_outputs = []
        for i, step in enumerate(steps, 1):
            result = self.execute_step(step, context=context)
            all_outputs.append(result)
            context += f"\nStep {i} Output: {result.get('output', '')}"

            if not result["success"]:
                self.logger.warning(f"⚠️ Step {i} failed: {result}")

        # Step 3: Self-audit
        audit = self.self_audit(goal, steps, context)

        # Step 4: Return full report
        return {
            "goal": goal,
            "steps": [s.dict() for s in steps],
            "outputs": all_outputs,
            "audit": audit,
            "success": all(r["success"] for r in all_outputs),
            "final_context": context
        }
