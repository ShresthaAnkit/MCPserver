from utils import validate_nepali_phone_number
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


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

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()