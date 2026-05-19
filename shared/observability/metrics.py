from __future__ import annotations

from collections import defaultdict
from time import perf_counter


class MetricsRegistry:
    """In-memory metrics registry with Prometheus-style text rendering."""

    def __init__(self) -> None:
        self.counters: dict[str, float] = defaultdict(float)
        self.gauges: dict[str, float] = {}
        self.latencies: dict[str, list[float]] = defaultdict(list)

    def inc(self, name: str, value: float = 1.0) -> None:
        self.counters[name] += value

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = value

    def observe_latency(self, name: str, seconds: float) -> None:
        self.latencies[name].append(seconds)

    def render(self) -> str:
        lines: list[str] = []
        for name, value in sorted(self.counters.items()):
            lines.append(f"{name} {value}")
        for name, value in sorted(self.gauges.items()):
            lines.append(f"{name} {value}")
        for name, values in sorted(self.latencies.items()):
            if values:
                lines.append(f"{name}_avg_seconds {sum(values) / len(values)}")
                lines.append(f"{name}_count {len(values)}")
        return "\n".join(lines) + "\n"


class LatencyTimer:
    def __init__(self, metrics: MetricsRegistry, name: str) -> None:
        self.metrics = metrics
        self.name = name
        self.started_at = 0.0

    def __enter__(self) -> "LatencyTimer":
        self.started_at = perf_counter()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.metrics.observe_latency(self.name, perf_counter() - self.started_at)
