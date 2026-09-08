"""
Run script for Si Sebel Bot.
Run this from the project root directory.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bot import main

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)