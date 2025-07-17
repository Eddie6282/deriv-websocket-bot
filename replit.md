# Deriv WebSocket Client

## Overview

This is a Python application that connects to the Deriv API WebSocket endpoint to stream real-time tick data for financial instruments, specifically the R_100 symbol. The application is built as a WebSocket client that can handle authentication, subscription management, and live data streaming from Deriv's trading platform.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Language**: Python 3
- **Communication Protocol**: WebSocket (WSS)
- **API Integration**: Deriv API v3
- **Design Pattern**: Single-threaded asynchronous event-driven architecture
- **Data Format**: JSON-based message exchange

### Key Design Decisions
- **Asynchronous Processing**: Uses `asyncio` and `websockets` for non-blocking I/O operations
- **Real-time Streaming**: Maintains persistent WebSocket connection for continuous data flow
- **Demo Mode Support**: Can operate with or without API token authentication
- **Error Handling**: Built-in reconnection logic with exponential backoff

## Key Components

### DerivWebSocketClient Class
- **Purpose**: Main client class that handles WebSocket connection lifecycle
- **Responsibilities**:
  - Connection management to Deriv API
  - Authentication handling (optional)
  - Subscription management for tick data
  - Reconnection logic with retry mechanisms
  - Message parsing and response handling

### Configuration Management
- **API Token**: Optional authentication token for live trading access
- **WebSocket URL**: Fixed endpoint to `wss://ws.deriv.com/websockets/v3`
- **Symbol Configuration**: Currently hardcoded to "R_100" symbol
- **Connection Parameters**: Configurable reconnection attempts and delays

### Logging System
- **Framework**: Python's built-in logging module
- **Output**: Console output with timestamps and log levels
- **Format**: Structured logging with datetime, level, and message

## Data Flow

### Connection Flow
1. Initialize client with optional API token
2. Establish WebSocket connection to Deriv API
3. Authenticate if token is provided (live mode)
4. Subscribe to tick data stream for specified symbol
5. Process incoming tick data continuously
6. Handle disconnections with automatic reconnection

### Message Structure
- **Outbound**: JSON requests with unique request IDs
- **Inbound**: JSON responses with tick data and status updates
- **Authentication**: Token-based authentication for live accounts
- **Subscription**: Real-time tick data for financial instruments

## External Dependencies

### Core Dependencies
- **websockets**: WebSocket client library for Python
- **asyncio**: Asynchronous I/O framework (built-in)
- **json**: JSON parsing and serialization (built-in)
- **logging**: Application logging (built-in)
- **datetime**: Timestamp handling (built-in)
- **typing**: Type hints for better code clarity (built-in)

### Third-party Services
- **Deriv API**: Primary external service for financial data
- **WebSocket Endpoint**: `wss://ws.deriv.com/websockets/v3`

## Deployment Strategy

### Environment Setup
- **Python Version**: Python 3.x required
- **Dependencies**: Install required packages via pip
- **Configuration**: Set API token via environment variable or direct initialization
- **Execution**: Run as standalone Python script

### Operating Modes
- **Demo Mode**: Runs without API token for testing and development
- **Live Mode**: Requires valid Deriv API token for real account access
- **Development**: Local execution with console logging
- **Production**: Can be containerized or deployed to cloud platforms

### Configuration Options
- **API Token**: Optional environment variable for authentication
- **Symbol Selection**: Currently hardcoded but can be made configurable
- **Reconnection Settings**: Adjustable retry attempts and delays
- **Logging Level**: Configurable via logging configuration

### Error Handling
- **Connection Failures**: Automatic reconnection with exponential backoff
- **Authentication Errors**: Graceful handling of invalid tokens
- **Data Processing**: Error handling for malformed messages
- **Network Issues**: Robust reconnection logic for unstable connections