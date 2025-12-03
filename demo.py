# demo.py (update this section)
from agents.executive_agent import ExecutiveAgent
from agents.tool_executor import ToolExecutor
from agents.tools.shell_tool import ShellTool
from agents.tools.web_browse import WebBrowseTool
from agents.tools.code_executor import CodeExecutorTool

# ... after loading aurora_base and memvault ...

# Initialize tools
tools = [
    ShellTool(sandboxed=True),
    WebBrowseTool(headless=True),
    CodeExecutorTool()
]

# Initialize agent
exec_agent = ExecutiveAgent(
    llm=aurora_base,
    tools=tools,
    memory=memvault,
    max_iterations=5
)

# Run a real goal
goal = "Write a Python script that fetches current weather in London via Open-Meteo API, saves to 'london_weather.csv', and prints summary."

print(f"\n🎯 GOAL: {goal}\n")
result = exec_agent.run(goal)

print("📋 PLAN:")
for step in result["steps"]:
    print(f"  {step['number']}. {step['description']}")

print("\n🧪 OUTPUTS:")
for i, out in enumerate(result["outputs"], 1):
    print(f"  Step {i}: {out.get('output', 'N/A')}")

print("\n🔍 SELF-AUDIT:")
print(result["audit"])
