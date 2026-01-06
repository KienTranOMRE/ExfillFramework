#!/bin/bash

# LC Form Auto-Fill System - Launcher Script

echo "========================================="
echo "LC Form Auto-Fill System"
echo "========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your GEMINI_API_KEY"
    echo ""
    echo "Example:"
    echo "GEMINI_API_KEY=your_api_key_here"
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "✓ Starting LC Form Auto-Fill System..."
echo "✓ The app will open in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the streamlit app
streamlit run app.py
