from fastmcp import FastMCP

mcp = FastMCP("Demo Server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


@mcp.tool()
def power(base: float, exponent: int) -> float:
    """Raise base to the power of exponent (e.g. 6^23). Always use this tool for exponentiation instead of computing it yourself."""
    return base ** exponent


@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse the characters in a string."""
    return text[::-1]


@mcp.tool()
def word_count(text: str) -> int:
    """Count the number of words in a string."""
    return len(text.split())


if __name__ == "__main__":
    mcp.run()