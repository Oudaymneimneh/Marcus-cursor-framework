#!/bin/bash
# Run AI evaluation from anywhere
# Usage: ./run_ai_evaluation.sh [--limit N] [--no-gemini]

# Get script directory (evaluation/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get project root (parent of evaluation/)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

echo "✅ Environment activated"
echo "📍 Working from: $SCRIPT_DIR"
echo ""

# Check if --no-gemini flag is present, otherwise skip Gemini by default
if [[ ! " $* " =~ " --no-gemini " ]]; then
    echo "💡 Tip: Using Claude + GPT-4 (Gemini skipped by default)"
    echo "   To include Gemini: remove --no-gemini flag"
    echo ""
fi

# Run the AI evaluation script (skip Gemini by default to avoid quota issues)
python "$SCRIPT_DIR/ai_raters.py" --no-gemini "$@"


