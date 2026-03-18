"""Classify tongue images into front and back using a trained model.

TODO: Integrate the actual classification model once the framework
(PyTorch / TensorFlow / ONNX) and input format are confirmed.
Currently uses a stub that treats all images as front images.
"""

from __future__ import annotations

import logging

import numpy as np

from ..base import PipelineContext, PipelineStep

logger = logging.getLogger(__name__)


class ClassifyStep(PipelineStep):
    name = "classify"
    description = "分類舌頭正反面影像"

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self._model = None

    def _load_model(self) -> None:
        """Load the classification model.

        Replace this method with actual model loading logic:
        - For ONNX:  onnxruntime.InferenceSession(self.model_path)
        - For PyTorch: torch.load(self.model_path)
        - For TF: tf.saved_model.load(self.model_path)
        """
        if self.model_path:
            logger.info("Model loading not yet implemented: %s", self.model_path)
        self._model = None  # placeholder

    def _predict(self, image: np.ndarray) -> str:
        """Predict whether an image is 'front' or 'back'.

        Replace this with actual model inference.
        Returns 'front' or 'back'.
        """
        # Stub: classify all as front until model is integrated
        return "front"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        if self._model is None:
            self._load_model()

        ctx.front_images = []
        ctx.back_images = []

        for i, img in enumerate(ctx.original_images):
            label = self._predict(img)
            if label == "front":
                ctx.front_images.append(img)
            else:
                ctx.back_images.append(img)
            logger.info("Image %d classified as: %s", i, label)

        ctx.results["classify"] = {
            "front_count": len(ctx.front_images),
            "back_count": len(ctx.back_images),
        }
        return ctx
