from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "platform_gateway"
for path in (str(ROOT), str(MODULE)):
    if path not in sys.path:
        sys.path.insert(0, path)
