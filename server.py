from starlette.middleware.cors import CORSMiddleware
from middleware import SmitheryConfigMiddleware
from utils import validate_nepali_phone_number
from mcp.server.fastmcp import FastMCP
from typing import Optional
import uvicorn
import os
# Create an MCP server
mcp = FastMCP("Demo")

# Optional: Handle configuration for backwards compatibility with stdio mode
# This function is only needed if you want to support stdio transport alongside HTTP
def handle_config(config: dict):
    """Handle configuration from Smithery - for backwards compatibility with stdio mode."""
    global _server_token, _case_sensitive
    if server_token := config.get('serverToken'):
        _server_token = server_token
    if case_sensitive := config.get('caseSensitive'):
        _case_sensitive = case_sensitive
# Store server token and case sensitivity for stdio mode (backwards compatibility)
_server_token: Optional[str] = None
_case_sensitive: Optional[bool] = None

def get_request_config() -> dict:
    """Get full config from current request context."""
    try:
        # Access the current request context from FastMCP
        import contextvars
        
        # Try to get from request context if available
        request = contextvars.copy_context().get('request')
        if hasattr(request, 'scope') and request.scope:
            return request.scope.get('smithery_config', {})
    except:
        pass
    
    # Return empty dict if no config found
    return {}
def get_config_value(key: str, default=None):
    """Get a specific config value from current request."""
    config = get_request_config()
    # Handle case where config might be None
    if config is None:
        config = {}
    return config.get(key, default)

def validate_server_access(server_token: Optional[str]) -> bool:
    """Validate server token - accepts any token for demo purposes."""
    # In a real app, you'd validate against your server's auth system
    # For demo purposes, we always return True
    return True

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def validatePhoneNumber(phone_number: str) -> bool:
    """Validates if the given phone number is a valid nepali phone number"""
    return validate_nepali_phone_number(phone_number)

@mcp.tool()
def checkBalance(phone_number: str) -> int:
    """Takes a validated phone number and return the balance of the user"""
    return 100

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main():
    transport_mode = os.getenv("TRANSPORT", "stdio")
    
    if transport_mode == "http":
        # HTTP mode with config extraction from URL parameters
        print("Character Counter MCP Server starting in HTTP mode...")
        
        # Setup Starlette app with CORS for cross-origin requests
        app = mcp.streamable_http_app()
        
        # IMPORTANT: add CORS middleware for browser based clients
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
            max_age=86400,
        )

        # Apply custom middleware for session config extraction
        app = SmitheryConfigMiddleware(app)

        # Use Smithery-required PORT environment variable
        port = int(os.environ.get("PORT", 8081))
        print(f"Listening on port {port}")

        uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
    
    else:
        # Optional: if you need backward compatibility, add stdio transport
        # You can publish this to uv for users to run locally
        print("Character Counter MCP Server starting in stdio mode...")
        
        server_token = os.getenv("SERVER_TOKEN")
        case_sensitive = os.getenv("CASE_SENSITIVE", "false").lower() == "true"
        # Set the server token and case sensitivity for stdio mode
        handle_config({"serverToken": server_token, "caseSensitive": case_sensitive})
        
        # Run with stdio transport (default)
        mcp.run()

if __name__ == "__main__":
    main()