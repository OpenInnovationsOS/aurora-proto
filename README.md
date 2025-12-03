cat > README.md << 'EOF'
# 🌐 AURORA-Proto v0.1  
**Q1 2026 Milestone**: Open-weight, agentic, self-hostable AI prototype.

## ✅ Features
- Foundation: `Qwen2.5-7B-Instruct` (AWQ quantized)
- Multimodal: Text + Image (Qwen2-VL)
- Agentic: Planner + Safe Tool Use (Shell, Web)
- Memory: FAISS + SQLite (AURORA-MemVault™)
- Code: Generation + Docker Sandbox
- Deploy: Local, Docker, Edge (GGUF)

## 🚀 Quick Start
```bash
git clone https://github.com/$(whoami)/aurora-proto.git
cd aurora-proto
pip install -r requirements.txt
playwright install chromium
python demo.py
