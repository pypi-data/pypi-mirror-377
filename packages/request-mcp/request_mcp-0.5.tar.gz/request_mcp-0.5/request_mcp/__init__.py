# __init__.py
# Expose main functions from core.py

# Import the obfuscated get_flag function
from .core import get_flag

# Optional: a simple hello function for testing or legacy code
def hello(name: str) -> str:
    """
    Simple test function.
    """
    return f"Hello, {name}!"

# Package version
__version__ = "0.1.0"

# Example usage:
# import request_mcp
# request_mcp.get_flag()  -> returns 'astalavista_baby'
# request_mcp.hello("World") -> returns 'Hello, World!'

