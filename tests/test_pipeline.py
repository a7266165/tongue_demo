"""Tests for the pipeline steps."""

from app.pipeline.base import PipelineContext
from app.pipeline.registry import PipelineRunner
from app.pipeline.steps import ClassifyStep, MaskStep, WhiteBalanceStep


def test_classify_step(sample_context):
    step = ClassifyStep()
    ctx = step.process(sample_context)
    # Stub classifies all as front
    assert len(ctx.front_images) == 1
    assert len(ctx.back_images) == 0
    assert "classify" in ctx.results


def test_mask_step(sample_context):
    # First classify
    classify = ClassifyStep()
    ctx = classify.process(sample_context)
    # Then mask
    mask = MaskStep()
    ctx = mask.process(ctx)
    assert "mask" in ctx.results
    assert ctx.results["mask"]["masks_created"] > 0


def test_white_balance_step(sample_context):
    classify = ClassifyStep()
    ctx = classify.process(sample_context)
    wb = WhiteBalanceStep()
    ctx = wb.process(ctx)
    assert "white_balance" in ctx.results


def test_full_pipeline(sample_context):
    runner = PipelineRunner()
    runner.register(ClassifyStep())
    runner.register(MaskStep())
    runner.register(WhiteBalanceStep())

    ctx = runner.run(sample_context)
    assert "classify" in ctx.results
    assert "mask" in ctx.results
    assert "white_balance" in ctx.results
    assert "_progress" in ctx.results
    assert len(ctx.results["_progress"]) == 3
