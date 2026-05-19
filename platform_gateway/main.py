from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.app import create_app
from config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(create_app(), host=settings.app_host, port=settings.app_port)


if __name__ == "__main__":
    main()
