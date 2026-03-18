from __future__ import annotations

import logging
from typing import Callable

from .base import PipelineContext, PipelineStep

logger = logging.getLogger(__name__)

# Callback signature: (step_name, context) -> None
StepCallback = Callable[[str, PipelineContext], None]


class PipelineRunner:
    """Manages and executes an ordered sequence of pipeline steps."""

    def __init__(self) -> None:
        self._steps: list[PipelineStep] = []

    def register(self, step: PipelineStep) -> None:
        """Add a step to the end of the pipeline."""
        self._steps.append(step)
        logger.info("Registered pipeline step: %s", step.name)

    @property
    def steps(self) -> list[PipelineStep]:
        return list(self._steps)

    def run(
        self,
        ctx: PipelineContext,
        on_step_complete: StepCallback | None = None,
    ) -> PipelineContext:
        """Execute all registered steps in order.

        Args:
            ctx: The pipeline context to process.
            on_step_complete: Optional callback invoked after each step
                finishes (used for WebSocket progress updates).
        """
        total = len(self._steps)
        for i, step in enumerate(self._steps, 1):
            if not step.validate(ctx):
                logger.info("Skipping step %s (validation failed)", step.name)
                continue

            logger.info("Running step %d/%d: %s", i, total, step.name)
            ctx = step.process(ctx)
            ctx.results.setdefault("_progress", []).append(
                {"step": step.name, "index": i, "total": total}
            )

            if on_step_complete:
                on_step_complete(step.name, ctx)

        return ctx
