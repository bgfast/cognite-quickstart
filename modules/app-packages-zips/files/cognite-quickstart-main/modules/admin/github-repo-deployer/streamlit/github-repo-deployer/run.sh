#!/bin/bash

# GitHub Repo to CDF Deployer - Launcher Script

echo "🚀 Starting GitHub Repo to CDF Deployer..."

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if cognite-toolkit is installed
if ! command -v cdf &> /dev/null; then
    echo "❌ Cognite toolkit not found. Installing..."
    pip install cognite-toolkit
fi

# Check for environment file
if [ -f "../../../../cdfenv.sh" ]; then
    echo "📁 Found cdfenv.sh, sourcing environment..."
    source ../../../../cdfenv.sh
fi

# Check for GitHub OAuth configuration
if [ -z "$GITHUB_CLIENT_ID" ] || [ -z "$GITHUB_CLIENT_SECRET" ]; then
    echo "⚠️  GitHub OAuth not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables for private repository access."
    echo "   Public repositories will still work without authentication."
fi

# Start the Streamlit app
echo "🌐 Starting Streamlit app..."
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
