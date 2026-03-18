"""Tongue region masking using HSV color thresholding.

Since the background is expected to be simple (tongue only),
HSV thresholding should work well. Can be upgraded to GrabCut
or a segmentation model if needed.
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

from ..base import PipelineContext, PipelineStep

logger = logging.getLogger(__name__)

# Default HSV range for tongue-like skin/tissue color
# These values may need tuning based on actual images
TONGUE_HSV_LOWER = np.array([0, 40, 60])
TONGUE_HSV_UPPER = np.array([25, 255, 255])


class MaskStep(PipelineStep):
    name = "mask"
    description = "舌頭區域遮罩"

    def __init__(
        self,
        hsv_lower: np.ndarray = TONGUE_HSV_LOWER,
        hsv_upper: np.ndarray = TONGUE_HSV_UPPER,
    ):
        self.hsv_lower = hsv_lower
        self.hsv_upper = hsv_upper

    def _create_mask(self, image: np.ndarray) -> np.ndarray:
        """Create a binary mask for the tongue region."""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        return mask

    def _apply_mask(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Apply mask to image, setting background to black."""
        return cv2.bitwise_and(image, image, mask=mask)

    def process(self, ctx: PipelineContext) -> PipelineContext:
        for i, img in enumerate(ctx.front_images):
            mask = self._create_mask(img)
            ctx.masks[f"front_{i}"] = mask
            ctx.intermediate_images[f"front_{i}_masked"] = self._apply_mask(img, mask)

        for i, img in enumerate(ctx.back_images):
            mask = self._create_mask(img)
            ctx.masks[f"back_{i}"] = mask
            ctx.intermediate_images[f"back_{i}_masked"] = self._apply_mask(img, mask)

        ctx.results["mask"] = {
            "masks_created": len(ctx.masks),
        }
        logger.info("Created %d masks", len(ctx.masks))
        return ctx
