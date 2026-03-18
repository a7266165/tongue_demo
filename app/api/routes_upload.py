"""Image upload API endpoint."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile

from ..pipeline.base import PipelineContext
from ..pipeline.registry import PipelineRunner
from ..storage.file_store import (
    generate_session_id,
    image_to_base64,
    save_image,
    save_results,
)
from ..config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["upload"])

# Pipeline runner is set from main.py during app startup
pipeline_runner: PipelineRunner | None = None


def set_pipeline(runner: PipelineRunner) -> None:
    global pipeline_runner
    pipeline_runner = runner


@router.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    """Upload one or more tongue images for analysis.

    Returns the session ID and analysis results.
    """
    session_id = generate_session_id()
    images: list[np.ndarray] = []

    for f in files:
        contents = await f.read()
        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is not None:
            images.append(img)
            save_image(img, settings.processed_dir / session_id, f.filename or "image.jpg")
        else:
            logger.warning("Failed to decode image: %s", f.filename)

    if not images:
        return {"error": "No valid images uploaded", "session_id": session_id}

    # Run pipeline
    ctx = PipelineContext(original_images=images)
    ctx.metadata["session_id"] = session_id
    ctx.metadata["filenames"] = [f.filename for f in files]

    if pipeline_runner:
        ctx = pipeline_runner.run(ctx)

    # Prepare response with base64 images
    response_images = {}
    for key, img in ctx.intermediate_images.items():
        if isinstance(img, np.ndarray):
            response_images[key] = image_to_base64(img)

    # Add front/back images to response
    for i, img in enumerate(ctx.front_images):
        response_images[f"front_{i}"] = image_to_base64(img)
    for i, img in enumerate(ctx.back_images):
        response_images[f"back_{i}"] = image_to_base64(img)

    # Save results
    result_data = {
        "session_id": session_id,
        "results": ctx.results,
        "image_count": len(images),
    }
    save_results(session_id, result_data)

    return {
        "session_id": session_id,
        "results": ctx.results,
        "images": response_images,
    }
