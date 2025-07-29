#!/bin/bash

# AI Resume Builder Setup Script

echo "🔧 Setting up AI Resume Builder"
echo "==============================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

node_version=$(node --version | grep -oP '\d+')
if [[ $node_version -lt 18 ]]; then
    echo "❌ Node.js 18+ required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv resume-env
source resume-env/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn sentence-transformers PyPDF2 spacy python-multipart

# Download spaCy model
echo "🧠 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Setup frontend
echo "🎨 Setting up frontend..."
cd resume-builder
npm install

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the development environment:"
echo "  ./start_dev.sh"
echo ""
echo "Or start services manually:"
echo "  Backend:  python run_backend.py"
echo "  Frontend: cd resume-builder && npm run dev"