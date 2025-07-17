#!/usr/bin/env python3
"""
Deriv WebSocket Client for Live Tick Data Streaming
Connects to Deriv API and streams real-time tick data for R_100 symbol
"""

import asyncio
import json
import logging
import os
import sys
import websockets
from datetime import datetime
from typing import Optional, Dict, Any
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DerivWebSocketClient:
    """
    WebSocket client for Deriv API to stream live tick data
    """
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.websocket_url = "wss://ws.deriv.com/websockets/v3"
        self.websocket = None
        self.is_connected = False
        self.is_authenticated = False
        self.is_subscribed = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5
        self.demo_mode = not bool(api_token)
        
        # Request IDs for tracking responses
        self.request_id = 1
        
        # Symbol to subscribe to
        self.symbol = "R_100"
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.shutdown())
        
    def get_next_request_id(self) -> int:
        """Generate next request ID"""
        self.request_id += 1
        return self.request_id
        
    async def connect(self) -> bool:
        """
        Connect to Deriv WebSocket API
        Returns True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to {self.websocket_url}...")
            
            self.websocket = await websockets.connect(
                self.websocket_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.is_connected = True
            self.reconnect_attempts = 0
            logger.info("✅ Connected to Deriv WebSocket API")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "No address associated with hostname" in error_msg:
                logger.error(f"❌ DNS resolution failed for {self.websocket_url}")
                logger.error("💡 This may be a network connectivity issue in the current environment")
                logger.error("💡 Please check if you have internet access or try again later")
            else:
                logger.error(f"❌ Connection failed: {e}")
            self.is_connected = False
            return False
            
    async def authenticate(self) -> bool:
        """
        Authenticate with Deriv API using token
        Returns True if authentication successful, False otherwise
        """
        if self.demo_mode:
            logger.info("🔓 Running in demo mode - skipping authentication")
            self.is_authenticated = True
            return True
            
        if not self.api_token:
            logger.error("❌ No API token provided for authentication")
            return False
            
        try:
            auth_request = {
                "authorize": self.api_token,
                "req_id": self.get_next_request_id()
            }
            
            logger.info("🔐 Authenticating with Deriv API...")
            await self.websocket.send(json.dumps(auth_request))
            
            # Wait for authentication response
            response = await self.websocket.recv()
            auth_response = json.loads(response)
            
            if auth_response.get("error"):
                error_msg = auth_response["error"].get("message", "Unknown error")
                logger.error(f"❌ Authentication failed: {error_msg}")
                return False
                
            if "authorize" in auth_response:
                self.is_authenticated = True
                logger.info("✅ Authentication successful")
                
                # Log account info if available
                if "loginid" in auth_response["authorize"]:
                    loginid = auth_response["authorize"]["loginid"]
                    logger.info(f"📊 Logged in as: {loginid}")
                    
                return True
            else:
                logger.error("❌ Unexpected authentication response")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
            
    async def subscribe_to_ticks(self) -> bool:
        """
        Subscribe to tick data for the specified symbol
        Returns True if subscription successful, False otherwise
        """
        try:
            tick_request = {
                "ticks": self.symbol,
                "subscribe": 1,
                "req_id": self.get_next_request_id()
            }
            
            logger.info(f"📈 Subscribing to {self.symbol} tick data...")
            await self.websocket.send(json.dumps(tick_request))
            
            # Wait for subscription confirmation
            response = await self.websocket.recv()
            tick_response = json.loads(response)
            
            if tick_response.get("error"):
                error_msg = tick_response["error"].get("message", "Unknown error")
                logger.error(f"❌ Subscription failed: {error_msg}")
                return False
                
            if "tick" in tick_response:
                self.is_subscribed = True
                logger.info(f"✅ Successfully subscribed to {self.symbol} ticks")
                
                # Process the first tick
                await self.process_tick(tick_response["tick"])
                return True
            else:
                logger.error("❌ Unexpected subscription response")
                return False
                
        except Exception as e:
            logger.error(f"❌ Subscription error: {e}")
            return False
            
    async def process_tick(self, tick_data: Dict[str, Any]):
        """
        Process and display tick data
        """
        try:
            symbol = tick_data.get("symbol", "N/A")
            quote = tick_data.get("quote", "N/A")
            epoch = tick_data.get("epoch", 0)
            
            # Convert epoch to readable timestamp
            if epoch:
                timestamp = datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            # Format the output
            print(f"🔴 {timestamp} | {symbol} | Quote: {quote}")
            
        except Exception as e:
            logger.error(f"❌ Error processing tick data: {e}")
            
    async def listen_for_messages(self):
        """
        Listen for incoming WebSocket messages
        """
        try:
            while self.is_connected and self.websocket:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=60  # 60 second timeout
                    )
                    
                    data = json.loads(message)
                    
                    # Handle tick data
                    if "tick" in data:
                        await self.process_tick(data["tick"])
                    
                    # Handle errors
                    elif "error" in data:
                        error_msg = data["error"].get("message", "Unknown error")
                        logger.error(f"❌ API Error: {error_msg}")
                        
                    # Handle other message types
                    else:
                        logger.debug(f"📨 Received message: {data}")
                        
                except asyncio.TimeoutError:
                    logger.warning("⏰ No message received within timeout, checking connection...")
                    if not self.websocket.open:
                        logger.error("❌ WebSocket connection lost")
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("⚠️ WebSocket connection closed")
                    break
                    
        except Exception as e:
            logger.error(f"❌ Error in message listener: {e}")
            
    async def reconnect(self) -> bool:
        """
        Attempt to reconnect to the WebSocket
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"❌ Max reconnection attempts ({self.max_reconnect_attempts}) reached")
            return False
            
        self.reconnect_attempts += 1
        logger.info(f"🔄 Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        await asyncio.sleep(self.reconnect_delay)
        
        if await self.connect():
            if await self.authenticate():
                if await self.subscribe_to_ticks():
                    return True
                    
        return False
        
    async def run(self):
        """
        Main run loop with reconnection logic
        """
        logger.info("🚀 Starting Deriv WebSocket Client...")
        
        if self.demo_mode:
            logger.warning("⚠️ Running in DEMO MODE - no real API token provided")
            logger.info("💡 Set DERIV_API_TOKEN environment variable for live trading")
            
        while True:
            try:
                # Initial connection
                if not await self.connect():
                    if not await self.reconnect():
                        break
                    continue
                    
                # Authentication
                if not await self.authenticate():
                    if not await self.reconnect():
                        break
                    continue
                    
                # Subscribe to ticks
                if not await self.subscribe_to_ticks():
                    if not await self.reconnect():
                        break
                    continue
                    
                # Listen for messages
                await self.listen_for_messages()
                
                # If we reach here, connection was lost
                logger.warning("⚠️ Connection lost, attempting to reconnect...")
                if not await self.reconnect():
                    break
                    
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                if not await self.reconnect():
                    break
                    
        await self.shutdown()
        
    async def shutdown(self):
        """
        Gracefully shutdown the client
        """
        logger.info("🔄 Shutting down WebSocket client...")
        
        try:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
                logger.info("✅ WebSocket connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing WebSocket: {e}")
            
        self.is_connected = False
        self.is_authenticated = False
        self.is_subscribed = False
        
        logger.info("👋 Deriv WebSocket Client shut down complete")

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  DERIV WEBSOCKET CLIENT                       ║
    ║                Live Tick Data Streaming                       ║
    ║                                                               ║
    ║  Symbol: R_100                                                ║
    ║  API: wss://ws.deriv.com/websockets/v3                       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main application entry point"""
    print_banner()
    
    # Get API token from environment variables
    api_token = os.getenv("DERIV_API_TOKEN")
    
    if not api_token:
        logger.warning("⚠️ DERIV_API_TOKEN environment variable not set")
        logger.info("💡 Running in demo mode - limited functionality")
        logger.info("💡 To use live data, set your API token:")
        logger.info("💡 export DERIV_API_TOKEN='your_token_here'")
        print()
        
        # Automatically continue in demo mode
        logger.info("🚀 Automatically continuing in demo mode...")
        print()
            
    # Create and run the client
    client = DerivWebSocketClient(api_token)
    
    try:
        await client.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Application interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        await client.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
