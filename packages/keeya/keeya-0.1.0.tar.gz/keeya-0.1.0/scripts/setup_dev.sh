#!/bin/bash
# Development setup script for Keeya

set -e

echo "🚀 Setting up Keeya development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install pytest pytest-cov black flake8 mypy

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Keeya Configuration
# Add your OpenRouter API key here
OPENROUTER_API_KEY=your_openrouter_key_here
EOF
    echo "⚠️  Please add your OpenRouter API key to .env file"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your OpenRouter API key to .env file"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run tests: python -m pytest tests/"
echo "4. Run example: python examples/basic_example.py"
echo ""
echo "Happy coding! 🚀"
