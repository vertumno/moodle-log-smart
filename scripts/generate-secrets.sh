#!/bin/bash
# generate-secrets.sh - Generate secure API keys for MoodleLogSmart

echo "🔐 MoodleLogSmart Secret Generator"
echo "==================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Generate API key
echo "Generating secure API key..."
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo ""
echo "✅ API Key Generated Successfully!"
echo ""
echo "Add this to your .env file:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API_KEYS=$API_KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ask if user wants to update .env file
read -p "Do you want to add this to .env file? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found. Creating from .env.example..."
        cp .env.example .env
    fi

    # Add API key to .env
    sed -i "s/^API_KEYS=.*/API_KEYS=$API_KEY/" .env

    if [ $? -eq 0 ]; then
        echo "✅ Updated .env with new API key"
    else
        echo "❌ Failed to update .env"
        echo "Please manually add: API_KEYS=$API_KEY"
        exit 1
    fi
else
    echo "ℹ️  You can manually add this to your .env file later"
fi

echo ""
echo "🔒 Keep your API keys secure!"
echo "   - Never commit .env to git"
echo "   - Rotate keys regularly in production"
echo "   - Use different keys for dev/staging/production"
echo ""
