"""Test configuration and fixtures."""

import numpy as np
import pytest

from app.pipeline.base import PipelineContext


@pytest.fixture
def sample_image() -> np.ndarray:
    """Create a simple test image (100x100, BGR)."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Add some tongue-like color in the center
    img[20:80, 20:80] = [100, 100, 200]  # BGR pinkish
    return img


@pytest.fixture
def sample_context(sample_image) -> PipelineContext:
    """Create a pipeline context with a sample image."""
    return PipelineContext(original_images=[sample_image])
