#!/usr/bin/env python3
"""Safely add the LOOM Ollama provider/model to Pi without touching other Pi state.

Only ~/.pi/agent/models.json (or $PI_CODING_AGENT_DIR/models.json) is created/updated.
Existing providers are preserved. auth.json, settings.json, sessions, skills, extensions,
and packages are never modified.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

MODEL_ID = "qwen3.5:4b-mlx"

DESIRED_PROVIDER = {
    "baseUrl": "http://localhost:11434/v1",
    "api": "openai-completions",
    "apiKey": "ollama",
    "compat": {
        "supportsDeveloperRole": False,
        "supportsReasoningEffort": False,
    },
    "models": [
        {
            "id": MODEL_ID,
            "name": "Qwen 3.5 4B MLX (Ollama / LOOM)",
            "reasoning": False,
            "input": ["text"],
            "contextWindow": 4096,
            "maxTokens": 2048,
            "cost": {
                "input": 0,
                "output": 0,
                "cacheRead": 0,
                "cacheWrite": 0,
            },
        }
    ],
}


def agent_dir() -> Path:
    override = os.environ.get("PI_CODING_AGENT_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".pi" / "agent"


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {"providers": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"ERROR: cannot parse existing {path}: {type(exc).__name__}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: existing {path} must contain a JSON object")
    providers = data.setdefault("providers", {})
    if not isinstance(providers, dict):
        raise SystemExit(f"ERROR: existing {path} has non-object 'providers'")
    return data


def merge_ollama(data: dict) -> tuple[dict, list[str]]:
    notes: list[str] = []
    providers = data.setdefault("providers", {})
    current = providers.get("ollama")

    if current is None:
        providers["ollama"] = DESIRED_PROVIDER
        notes.append("added providers.ollama")
        return data, notes

    if not isinstance(current, dict):
        raise SystemExit("ERROR: existing providers.ollama is not a JSON object; refusing to overwrite it")

    # Preserve every existing Ollama field. Add LOOM defaults only where absent.
    for key in ("baseUrl", "api", "apiKey", "compat"):
        if key not in current:
            current[key] = DESIRED_PROVIDER[key]
            notes.append(f"added missing providers.ollama.{key}")

    models = current.setdefault("models", [])
    if not isinstance(models, list):
        raise SystemExit("ERROR: existing providers.ollama.models is not an array; refusing to overwrite it")

    existing_model = next(
        (m for m in models if isinstance(m, dict) and m.get("id") == MODEL_ID),
        None,
    )
    if existing_model is None:
        models.append(DESIRED_PROVIDER["models"][0])
        notes.append(f"added model {MODEL_ID}")
    else:
        desired_model = DESIRED_PROVIDER["models"][0]
        for key, value in desired_model.items():
            if key not in existing_model:
                existing_model[key] = value
                notes.append(f"added missing field {MODEL_ID}.{key}")
        notes.append(f"preserved existing configuration for model {MODEL_ID}")

    return data, notes


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix="models.json.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def main() -> int:
    root = agent_dir()
    path = root / "models.json"
    existed = path.exists()
    data = load_existing(path)

    backup = None
    if existed:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = root / f"models.json.bak-{stamp}"
        shutil.copy2(path, backup)

    data, notes = merge_ollama(data)
    atomic_write(path, data)

    print("LOOM Pi Ollama provider merge complete")
    print(f"models.json: {path}")
    print(f"backup: {backup if backup else 'not needed (file did not previously exist)'}")
    for note in notes:
        print(f"- {note}")
    print("Untouched: auth.json, settings.json, sessions, skills, extensions, packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
