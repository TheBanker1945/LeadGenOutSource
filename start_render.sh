#!/bin/bash
# Render startup script
# This runs automatically when your app starts on Render

echo "🚀 Starting Lead Generation Dashboard on Render..."

# Initialize database with tokens and usage
echo "📊 Fixing authentication tokens..."
python force_fix_tokens.py

# Start the Streamlit dashboard
echo "🌐 Starting Streamlit..."
streamlit run login.py --server.port=10000 --server.address=0.0.0.0
