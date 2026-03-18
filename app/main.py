"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import cv2
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import routes_analysis, routes_upload, ws
from .camera.watcher import FolderWatcher
from .config import settings
from .pipeline.base import PipelineContext
from .pipeline.registry import PipelineRunner
from .pipeline.steps import ClassifyStep, MaskStep, WhiteBalanceStep
from .storage.file_store import generate_session_id, save_results

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Build the pipeline
pipeline = PipelineRunner()
pipeline.register(ClassifyStep(model_path=str(settings.model_path)))
pipeline.register(MaskStep())
pipeline.register(WhiteBalanceStep())

# Share pipeline with upload route
routes_upload.set_pipeline(pipeline)


def handle_new_image(image_path: Path) -> None:
    """Called by the folder watcher when a new image arrives."""
    logger.info("Processing new image from watcher: %s", image_path.name)
    img = cv2.imread(str(image_path))
    if img is None:
        logger.error("Failed to read image: %s", image_path)
        return

    session_id = generate_session_id()
    ctx = PipelineContext(original_images=[img])
    ctx.metadata["session_id"] = session_id
    ctx.metadata["source"] = "watcher"
    ctx.metadata["filename"] = image_path.name

    ctx = pipeline.run(ctx)

    save_results(session_id, {
        "session_id": session_id,
        "results": ctx.results,
        "source": "watcher",
        "filename": image_path.name,
    })
    logger.info("Watcher processing complete: session=%s", session_id)


# Folder watcher instance
watcher = FolderWatcher(
    watch_dir=settings.incoming_dir,
    on_new_image=handle_new_image,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    settings.ensure_dirs()
    watcher.start()
    logger.info("Tongue Analysis System started")
    yield
    watcher.stop()
    logger.info("Tongue Analysis System stopped")


app = FastAPI(
    title="舌頭即時分析系統",
    description="Tongue Image Analysis System",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routes
app.include_router(routes_upload.router)
app.include_router(routes_analysis.router)
app.include_router(ws.router)

# Serve static files (frontend)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
