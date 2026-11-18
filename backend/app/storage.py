import json
import threading
from pathlib import Path
from typing import Any, Iterable


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
_lock = threading.RLock()


def _path(name: str) -> Path:
    if not name.endswith(".json"):
        name += ".json"
    return DATA_DIR / name


def load(name: str, default: Any = None) -> Any:
    path = _path(name)
    with _lock:
        if not path.exists():
            return [] if default is None else default
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def save(name: str, value: Any) -> None:
    path = _path(name)
    with _lock:
        temp = path.with_suffix(".json.tmp")
        with temp.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.flush()
        temp.replace(path)


def append(name: str, item: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        items = load(name, [])
        items.append(item)
        save(name, items)
    return item


def update_by_id(name: str, item_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
    with _lock:
        items = load(name, [])
        for index, item in enumerate(items):
            if item.get("id") == item_id:
                updated = {**item, **changes}
                items[index] = updated
                save(name, items)
                return updated
    return None


def next_sequential_id(name: str, prefix: str) -> str:
    with _lock:
        items = load(name, [])
        numbers = []
        for item in items:
            value = str(item.get("id", ""))
            if value.startswith(prefix):
                try:
                    numbers.append(int(value[len(prefix):]))
                except ValueError:
                    pass
        return f"{prefix}{max(numbers, default=0) + 1:04d}"
