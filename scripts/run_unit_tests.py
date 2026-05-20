from __future__ import annotations

import subprocess
import sys

SUITES = [
    (".", ["shared/tests", "tests"]),
    ("scraper_engine", ["tests"]),
    ("adaptive_ai_layer", ["tests"]),
    ("algo_trading_lab", ["tests"]),
    ("platform_gateway", ["tests"]),
]


def main() -> int:
    status = 0
    for cwd, args in SUITES:
        result = subprocess.call([sys.executable, "-m", "pytest", *args], cwd=cwd)
        status = status or result
    return status


if __name__ == "__main__":
    raise SystemExit(main())
