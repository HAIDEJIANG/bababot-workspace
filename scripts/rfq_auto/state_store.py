from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict


@dataclass
class RunState:
    run_id: str
    current_index: int = 0
    completed: bool = False
    meta: Dict[str, Any] | None = None


class StateStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, default: RunState) -> RunState:
        if not self.path.exists():
            return default
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return RunState(
            run_id=data.get("run_id", default.run_id),
            current_index=int(data.get("current_index", 0)),
            completed=bool(data.get("completed", False)),
            meta=data.get("meta") or {},
        )

    def save(self, state: RunState) -> None:
        self.path.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")
