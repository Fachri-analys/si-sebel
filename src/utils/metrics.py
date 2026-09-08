"""Small in-process metrics registry for health and operational reporting."""

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict


@dataclass
class Metrics:
    """Thread-safe counters with no user content or identifiers."""

    _counters: Dict[str, int] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def increment(self, name: str, amount: int = 1) -> None:
        if not name or amount < 0:
            raise ValueError("Metric name must be non-empty and amount non-negative")
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount

    def snapshot(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._counters)


metrics = Metrics()
