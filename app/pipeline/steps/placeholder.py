"""Placeholder step template for future analysis modules.

Copy this file and modify to create new analysis steps.
"""

from __future__ import annotations

import logging

from ..base import PipelineContext, PipelineStep

logger = logging.getLogger(__name__)


class PlaceholderStep(PipelineStep):
    name = "placeholder"
    description = "佔位步驟（範本）"

    def validate(self, ctx: PipelineContext) -> bool:
        # Disabled by default; set to True when implementing
        return False

    def process(self, ctx: PipelineContext) -> PipelineContext:
        # Add your analysis logic here
        # Example:
        #   result = analyze(ctx.front_images)
        #   ctx.results["my_analysis"] = result
        logger.info("Placeholder step executed (no-op)")
        return ctx
