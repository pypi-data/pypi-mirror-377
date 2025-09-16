"""Entry point for the game collection package."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import after path modification
from game.main import main  # noqa: E402

if __name__ == "__main__":
    main()
