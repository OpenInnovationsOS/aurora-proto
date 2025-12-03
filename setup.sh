# setup.sh
#!/bin/bash
echo "🚀 Setting up AURORA-Proto v0.1..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.10+ not found. Install it first."
    exit 1
fi

# Create virtual env (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install core deps
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Download Qwen2.5-7B-Instruct AWQ (if not cached)
echo "📦 Downloading Qwen2.5-7B-Instruct (AWQ quantized)..."
python -c "
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct')
print('✅ Model downloaded.')
"

echo "🎉 Setup complete! Run:"
echo "   source .venv/bin/activate"
echo "   python demo.py"
