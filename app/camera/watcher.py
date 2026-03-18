"""Filesystem watcher that triggers the pipeline when new images arrive."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


class ImageHandler(FileSystemEventHandler):
    """Handles new image files in the watched directory."""

    def __init__(self, on_new_image: Callable[[Path], None]):
        self.on_new_image = on_new_image

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            logger.info("New image detected: %s", path.name)
            self.on_new_image(path)


class FolderWatcher:
    """Watches a directory for new image files."""

    def __init__(self, watch_dir: Path, on_new_image: Callable[[Path], None]):
        self.watch_dir = watch_dir
        self.handler = ImageHandler(on_new_image)
        self._observer: Observer | None = None

    def start(self) -> None:
        """Start watching the directory."""
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self._observer = Observer()
        self._observer.schedule(self.handler, str(self.watch_dir), recursive=False)
        self._observer.start()
        logger.info("Watching directory: %s", self.watch_dir)

    def stop(self) -> None:
        """Stop watching."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("Stopped watching directory")
