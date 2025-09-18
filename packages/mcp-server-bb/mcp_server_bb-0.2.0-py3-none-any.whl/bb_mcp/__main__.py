import atexit
import asyncio

from .bb_mcp import mcp, service
from .config import settings


def _close_service() -> None:
    try:
        asyncio.run(service.close())
    except RuntimeError:
        # Event loop already running – best effort close.
        pass


def main() -> None:
    print("BB_BASE_URL:", settings.bb_base_url)
    print("Starting BB MCP server...")
    atexit.register(_close_service)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
