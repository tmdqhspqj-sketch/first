from pathlib import Path
from typing import Any

import yaml

from app.settings import settings


def _load_yaml_dir(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if "id" not in data:
            data["id"] = path.stem
        items.append(data)
    return items


def list_personas() -> list[dict[str, Any]]:
    return _load_yaml_dir(settings.config_path / "personas")


def list_models() -> list[dict[str, Any]]:
    return _load_yaml_dir(settings.config_path / "models")


def get_persona(persona_id: str) -> dict[str, Any] | None:
    for p in list_personas():
        if p.get("id") == persona_id:
            return p
    return None


def get_model(model_id: str) -> dict[str, Any] | None:
    for m in list_models():
        if m.get("id") == model_id:
            return m
    return None
