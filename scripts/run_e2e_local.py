from __future__ import annotations

import subprocess
import sys


def main() -> int:
    return subprocess.call([sys.executable, "-m", "pytest", "tests/test_real_local_pipeline.py", "-q"])


if __name__ == "__main__":
    raise SystemExit(main())
