"""White balance correction using the gray-world algorithm.

Can be extended to use a color reference card if one is present
in the image.
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

from ..base import PipelineContext, PipelineStep

logger = logging.getLogger(__name__)


class WhiteBalanceStep(PipelineStep):
    name = "white_balance"
    description = "白平衡校正"

    @staticmethod
    def _gray_world(image: np.ndarray) -> np.ndarray:
        """Apply gray-world white balance.

        Adjusts each channel so that the average color is gray.
        """
        result = image.astype(np.float32)
        avg_b = np.mean(result[:, :, 0])
        avg_g = np.mean(result[:, :, 1])
        avg_r = np.mean(result[:, :, 2])
        avg_all = (avg_b + avg_g + avg_r) / 3.0

        if avg_b > 0:
            result[:, :, 0] *= avg_all / avg_b
        if avg_g > 0:
            result[:, :, 1] *= avg_all / avg_g
        if avg_r > 0:
            result[:, :, 2] *= avg_all / avg_r

        return np.clip(result, 0, 255).astype(np.uint8)

    def _correct(self, image: np.ndarray) -> np.ndarray:
        """Apply white balance correction to an image."""
        return self._gray_world(image)

    def process(self, ctx: PipelineContext) -> PipelineContext:
        ctx.front_images = [self._correct(img) for img in ctx.front_images]
        ctx.back_images = [self._correct(img) for img in ctx.back_images]

        # Also update intermediate masked images if they exist
        for key in list(ctx.intermediate_images.keys()):
            if key.endswith("_masked"):
                ctx.intermediate_images[key] = self._correct(
                    ctx.intermediate_images[key]
                )

        ctx.results["white_balance"] = {"method": "gray_world"}
        logger.info("White balance applied (gray-world)")
        return ctx
