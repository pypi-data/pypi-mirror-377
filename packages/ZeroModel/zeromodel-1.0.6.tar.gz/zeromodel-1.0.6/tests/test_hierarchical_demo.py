# tests/test_hierarchical_demo.py
import os
import numpy as np
import logging

from zeromodel.pipeline.executor import PipelineExecutor

logger = logging.getLogger(__name__)

def test_hierarchical_demo(tmp_path):
    """
    Demonstration test:
    Run HierarchicalView on synthetic data and capture a GIF of each zoom level.
    """
    # synthetic docs x metrics
    N, M = 128, 64
    rng = np.random.default_rng(42)
    X = np.clip(rng.normal(0.5, 0.25, size=(N, M)), 0, 1).astype(np.float32)

    out_gif  = str(tmp_path / "hierarchical_zoom.gif")

    stages = [
        {"stage": "normalizer/normalize.NormalizeStage", "params": {}},
        {"stage": "organizer/hierarchical_view.HierarchicalView", "params": {
            "levels": 6,                # max depth to attempt
            "row_frac": 0.5, 
            "col_frac": 0.5,
            "window_mode": "quadrants",
            "norm_mode": "local_subset",
            "alpha": 0.97,
            "beam_size": 1,
            "early_stop_epsilon": 1e-6,
            "top_left_params": {
                "metric_mode": "mean",
                "iterations": 6,
                "monotone_push": True,
                "reverse": True,
                "clip_percent": 0.005,
                "stretch": True,
                "push_corner": "tl"
            }
        }},
        {"stage": "vpm/write.VPMWrite", "params": {
            "output_path": str(tmp_path / "hierarchical_final.png")
        }},
    ]

    context = {
        "enable_gif": True,
        "gif_path": out_gif,
        "gif_scale": 3,   # enlarge tiles for visibility
        "gif_fps": 2,     # slow playback so levels are visible
    }

    result, ctx = PipelineExecutor(stages).run(X, context=context)

    # Verify
    assert "hierview" in ctx
    n_levels = len(ctx["hierview"]["levels"])
    logger.info(f"HierarchicalView ran for {n_levels} levels")

    assert os.path.exists(out_gif), "GIF file was not created"
    assert os.path.getsize(out_gif) > 0, "GIF is empty"

    logger.info(f"Hierarchical GIF written to {out_gif}")
    logger.info(f"Final matrix shape: {result.shape}")
    logger.info(f"All recorded shapes: {[lvl['shape'] for lvl in ctx['hierview']['levels']]}")

def test_hierarchical_sorted_gif(tmp_path):
    """
    Demonstration test:
    Run HierarchicalView and capture both the sorting and zooming
    at each level into a GIF animation.
    """
    # synthetic docs x metrics
    N, M = 96, 48
    rng = np.random.default_rng(7)
    X = np.clip(rng.normal(0.5, 0.25, size=(N, M)), 0, 1).astype(np.float32)

    out_gif = str(tmp_path / "hierarchical_sorted.gif")

    stages = [
        {"stage": "normalizer/normalize.NormalizeStage", "params": {}},
        {"stage": "organizer/hierarchical_view.HierarchicalView", "params": {
            "levels": 4,
            "row_frac": 0.5, "col_frac": 0.5,
            "window_mode": "quadrants",
            "norm_mode": "local_subset",
            "alpha": 0.97,
            "beam_size": 1,
            "early_stop_epsilon": 1e-6,
            "top_left_params": {
                "metric_mode": "mean",
                "iterations": 4,
                "monotone_push": True,
                "reverse": True,
                "clip_percent": 0.01,
                "stretch": True,
                "push_corner": "tl"
            },
            # NEW: tell HierarchicalView to capture both
            "record_sorted": True,   # full matrix after sorting
            "record_zoomed": True    # extracted quadrant
        }},
        {"stage": "vpm/write.VPMWrite", "params": {
            "output_path": str(tmp_path / "hierarchical_final.png")
        }},
    ]

    context = {
        "enable_gif": True,
        "gif_path": out_gif,
        "gif_scale": 3,
        "gif_fps": 2,
    }

    result, ctx = PipelineExecutor(stages).run(X, context=context)

    # Verify hierarchical metadata
    assert "hierview" in ctx
    levels = ctx["hierview"]["levels"]
    logger.info(f"HierarchicalView ran {len(levels)} levels")
    for i, lvl in enumerate(levels):
        logger.info(
            f"Level {i}: sorted={lvl['sorted'].shape}, zoomed={lvl['extracted'].shape}"
        )

    assert os.path.exists(out_gif), "GIF was not created"
    assert os.path.getsize(out_gif) > 0, "GIF is empty"

    logger.info(f"Hierarchical sorted+zoom GIF written to {out_gif}")
