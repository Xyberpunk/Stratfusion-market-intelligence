from __future__ import annotations

import os
import sys

import httpx

CHECKS = [
    ("gateway", "http://127.0.0.1:8070/health", True),
    ("adaptive_ai", "http://127.0.0.1:8090/health", False),
    ("algo_lab", "http://127.0.0.1:8080/health", False),
    ("dashboard", "http://127.0.0.1:8060", False),
]


def main() -> int:
    failed = False
    with httpx.Client(timeout=5) as client:
        for name, url, required in CHECKS:
            try:
                response = client.get(url)
                status = "PASS" if response.status_code < 500 else "WARN"
                print(f"{status} {name}: {response.status_code} {url}")
                failed = failed or (required and response.status_code >= 500)
            except Exception as exc:
                status = "FAIL" if required else "WARN"
                print(f"{status} {name}: {exc}")
                failed = failed or required
    if os.getenv("MYSQL_ENABLED", "false").lower() in {"1", "true", "yes"}:
        print("WARN mysql: enabled in env but not checked by local smoke script")
    if os.getenv("ENABLE_KAFKA", "false").lower() in {"1", "true", "yes"}:
        print("WARN kafka: enabled in env but not required for local synchronous smoke")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
