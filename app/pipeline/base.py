from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class PipelineContext:
    """Data container that flows through every pipeline step.

    Each step reads from and writes to this context.
    """

    # Input images (multiple photos from one session)
    original_images: list[np.ndarray] = field(default_factory=list)

    # Classified images
    front_images: list[np.ndarray] = field(default_factory=list)
    back_images: list[np.ndarray] = field(default_factory=list)

    # Masks keyed by image identifier
    masks: dict[str, np.ndarray] = field(default_factory=dict)

    # Arbitrary metadata (e.g. filenames, timestamps)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Analysis results from each step
    results: dict[str, Any] = field(default_factory=dict)

    # Intermediate images for visualization (base64 or ndarray)
    intermediate_images: dict[str, Any] = field(default_factory=dict)


class PipelineStep(ABC):
    """Abstract base class for all pipeline steps."""

    name: str = "unnamed"
    description: str = ""

    @abstractmethod
    def process(self, ctx: PipelineContext) -> PipelineContext:
        """Execute this step, modifying and returning the context."""
        ...

    def validate(self, ctx: PipelineContext) -> bool:
        """Optional pre-check. Return False to skip this step."""
        return True
