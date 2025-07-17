#!/bin/bash
# Deriv WebSocket Client Setup Script

echo "Setting up Deriv WebSocket Client..."

# Create project directory
mkdir -p deriv_websocket_client
cd deriv_websocket_client

# Install Python dependencies
echo "Installing dependencies..."
pip install websockets

echo "Setup complete!"
echo ""
echo "To run the client:"
echo "1. Set your API token: export DERIV_API_TOKEN='your_token_here'"
echo "2. Run: python main.py"
echo ""
echo "Or copy the main.py file content from your Replit project."