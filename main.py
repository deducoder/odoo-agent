from server import mcp  # Importa clase `mcp` desde el módulo `server`

import tools.health  # Importa función `health` desde tools
import tools.common.get_order  # Importa función `get_order` desde tools
import tools.common.get_order_line  # Importa función `get_order_line` desde tools

if __name__ == "__main__":
    mcp.run()  # Llama al método `run*()` de la instancia `mcp`
