# vscode-extension/api_server.py
from flask import Flask, request, jsonify
from demo import main as run_agent

app = Flask(__name__)

@app.route('/agent', methods=['POST'])
def agent():
    data = request.get_json()
    goal = data.get('goal', '')

    # Here you’d call the actual agent — for demo, we simulate
    # In real impl, you’d import ExecutiveAgent and run it
    result = {
        "goal": goal,
        "audit": "✅ Goal achieved. No unsafe actions. Output complete.",
        "steps": [{"number": 1, "description": "Generated code"}],
        "outputs": [{"success": True, "output": "print('Hello from AURORA')"}]
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
