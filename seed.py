"""Top-level shim so `python seed.py --input <yaml> --db <sqlite>` works from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sdlc_mcp.seed import main  # noqa: E402


if __name__ == "__main__":
    sys.exit(main())
