from __future__ import annotations

import uvicorn

from api.app import create_app
from config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(create_app(), host=settings.app_host, port=settings.app_port)


if __name__ == "__main__":
    main()
