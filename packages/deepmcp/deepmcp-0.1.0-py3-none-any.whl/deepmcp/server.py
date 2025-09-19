from fastmcp import FastMCP

mcp = FastMCP("Calculator MCP Server")


@mcp.tool
def add(a: float, b: float) -> float:
    """Adds two numbers (int or float)."""
    return a + b

@mcp.tool
def subtract(a: float, b: float) -> float:
    """Subtracts two numbers (int or float)."""
    return a - b

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers (int or float)."""
    return a * b

@mcp.tool
def divide(a: float, b: float) -> float:
    """Divides two numbers (int or float)."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

@mcp.tool
def power(base: float, exponent: float) -> float:
    """Raises a number to the power of another number."""
    return base ** exponent

def main():
    mcp.run()

if __name__ == "__main__":
    main()