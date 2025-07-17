# Deriv WebSocket Client

A Python WebSocket client for streaming live tick data from Deriv API with authentication and error handling.

## Features

- **Real-time WebSocket Connection**: Connects to `wss://ws.deriv.com/websockets/v3`
- **API Token Authentication**: Uses `DERIV_API_TOKEN` environment variable
- **Live R_100 Tick Streaming**: Automatically subscribes to R_100 symbol tick data
- **Demo Mode Support**: Works without API token for testing
- **Robust Error Handling**: Automatic reconnection with exponential backoff
- **Graceful Shutdown**: Handles interrupts and signals properly

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install websockets
   ```

## Usage

### With API Token (Live Trading Data)
1. Get your Deriv API token from your account settings
2. Set the environment variable:
   ```bash
   export DERIV_API_TOKEN='your_token_here'
   ```
3. Run the client:
   ```bash
   python main.py
   ```

### Demo Mode
Simply run without setting the API token:
```bash
python main.py
```

## Expected Output

When successfully connected, you'll see:
```
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  DERIV WEBSOCKET CLIENT                       ║
    ║                Live Tick Data Streaming                       ║
    ║                                                               ║
    ║  Symbol: R_100                                                ║
    ║  API: wss://ws.deriv.com/websockets/v3                       ║
    ╚═══════════════════════════════════════════════════════════════╝

2025-07-16 18:42:39 - INFO - 🚀 Starting Deriv WebSocket Client...
2025-07-16 18:42:39 - INFO - ✅ Connected to Deriv WebSocket API
2025-07-16 18:42:39 - INFO - ✅ Authentication successful
2025-07-16 18:42:39 - INFO - ✅ Successfully subscribed to R_100 ticks

🔴 2025-07-16 18:42:40 | R_100 | Quote: 1234.56
🔴 2025-07-16 18:42:41 | R_100 | Quote: 1234.78
🔴 2025-07-16 18:42:42 | R_100 | Quote: 1234.90
...
```

## Network Connectivity

If you encounter DNS resolution issues, ensure:
- Internet connectivity is available
- No firewall blocking WebSocket connections
- DNS can resolve `ws.deriv.com`

## Error Handling

The client includes comprehensive error handling:
- Automatic reconnection on connection loss
- Graceful handling of authentication failures
- Clear error messages for troubleshooting
- Exponential backoff for reconnection attempts

## Configuration

You can modify the following in `main.py`:
- `symbol`: Change from "R_100" to other Deriv symbols
- `max_reconnect_attempts`: Adjust reconnection retry limit
- `reconnect_delay`: Change delay between reconnection attempts

## Deployment

This client can be deployed to:
- Local development environments
- Cloud platforms (AWS, GCP, Azure)
- Container platforms (Docker, Kubernetes)
- VPS/dedicated servers

Ensure the deployment environment has:
- Python 3.7+
- Internet connectivity
- Environment variable support for API token