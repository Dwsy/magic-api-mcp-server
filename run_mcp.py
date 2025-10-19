#!/usr/bin/env python3
"""MCP Service Entry Point - FastMCP Run Mode"""

import signal
import sys
import atexit
from magicapi_mcp.magicapi_assistant import create_app
from magicapi_mcp.settings import DEFAULT_SETTINGS

# Create global mcp object for fastmcp command
mcp = create_app()

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to ensure graceful shutdown"""
    print('\nShutting down server...')
    _cleanup_resources()
    print('Server has been shut down')
    sys.exit(0)

def _cleanup_resources():
    """Clean up resources, especially the WebSocket manager"""
    # Get context from tool registry
    from magicapi_mcp.tool_registry import tool_registry
    
    if tool_registry.context:
        # Get and shut down WebSocket manager
        try:
            ws_manager = tool_registry.context.ws_manager
            if ws_manager and hasattr(ws_manager, 'stop_sync'):
                ws_manager.stop_sync()
                print('WebSocket manager has been shut down')
        except Exception as e:
            print('Error shutting down WebSocket manager: ' + str(e))
        
        # Clean up resource manager
        try:
            resource_manager = tool_registry.context.resource_manager
            if resource_manager and hasattr(resource_manager, 'close'):
                resource_manager.close()
        except Exception as e:
            print('Error shutting down resource manager: ' + str(e))

def setup_signal_handlers():
    """Setup signal handlers to ensure graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination

# Register cleanup function on exit
def cleanup_on_exit():
    """Cleanup function called on program exit"""
    _cleanup_resources()

if __name__ == '__main__':
    # Setup signal handlers
    setup_signal_handlers()
    
    # Register exit cleanup function
    atexit.register(cleanup_on_exit)
    
    try:
        # When running this script directly, use stdio transport (this is FastMCP's standard mode)
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print('Server error: ' + str(e))
        _cleanup_resources()
        sys.exit(1)
