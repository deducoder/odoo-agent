from server import mcp  # Importa clase `mcp` desde el módulo `server`


@mcp.tool()  # El decorador `@mcp.tool` registra la función `health` como una herramienta
def health() -> str:
    """
    Verifica estado del servidor MCP
    """
    return "MCP server OK"
