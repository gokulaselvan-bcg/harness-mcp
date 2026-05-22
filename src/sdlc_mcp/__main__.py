"""Entry point: `python -m sdlc_mcp` runs the MCP server over stdio."""
from __future__ import annotations

import sys

from .server import build_server


def main() -> int:
    server = build_server()
    server.run()  # stdio transport by default
    return 0


if __name__ == "__main__":
    sys.exit(main())
