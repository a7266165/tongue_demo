"""File-based storage for images and analysis results."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from ..config import settings


def generate_session_id() -> str:
    """Generate a unique session ID based on timestamp + short UUID."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:6]
    return f"{ts}_{short_id}"


def save_image(image: np.ndarray, directory: Path, filename: str) -> Path:
    """Save an image to disk and return the file path."""
    directory.mkdir(parents=True, exist_ok=True)
    filepath = directory / filename
    cv2.imwrite(str(filepath), image)
    return filepath


def save_results(session_id: str, results: dict) -> Path:
    """Save analysis results as JSON."""
    results_dir = settings.results_dir / session_id
    results_dir.mkdir(parents=True, exist_ok=True)
    filepath = results_dir / "results.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return filepath


def load_results(session_id: str) -> dict | None:
    """Load analysis results for a given session."""
    filepath = settings.results_dir / session_id / "results.json"
    if not filepath.exists():
        return None
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def list_sessions() -> list[str]:
    """List all session IDs with results."""
    results_dir = settings.results_dir
    if not results_dir.exists():
        return []
    return sorted(
        [d.name for d in results_dir.iterdir() if d.is_dir()],
        reverse=True,
    )


def image_to_base64(image: np.ndarray, fmt: str = ".jpg") -> str:
    """Encode an image as a base64 data URI string."""
    import base64

    _, buffer = cv2.imencode(fmt, image)
    b64 = base64.b64encode(buffer).decode("utf-8")
    mime = "image/jpeg" if fmt == ".jpg" else "image/png"
    return f"data:{mime};base64,{b64}"
