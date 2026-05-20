from __future__ import annotations

import compileall
import pathlib
import sys

MODULES = ["scraper_engine", "adaptive_ai_layer", "algo_trading_lab", "platform_gateway", "shared"]
EXCLUDES = {".venv", "__pycache__", ".pytest_cache", "chroma_db"}


def main() -> int:
    ok = True
    for module in MODULES:
        files = [
            str(path)
            for path in pathlib.Path(module).rglob("*.py")
            if not any(part in EXCLUDES for part in path.parts)
        ]
        ok = compileall.compile_file(*files, quiet=1) and ok if len(files) == 1 else ok
        for file_path in files:
            ok = compileall.compile_file(file_path, quiet=1) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
