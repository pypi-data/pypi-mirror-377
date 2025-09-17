# zeromodel/tools/gif_logger.py

from __future__ import annotations
import time
import numpy as np
from PIL import Image, ImageDraw

class GifLogger:
    def __init__(self, max_frames=2000, vpm_scale=4, strip_h=40, bg=(10, 10, 12), fps: int | None = None, **kwargs):
        """
        Backward-compatible init:
        - Accepts optional fps (some callers pass fps=...)
        - **kwargs is ignored to remain forwards-compatible with older/newer call sites.
        """
        self.frames = []
        self.meta = []  # store dicts of metrics for bottom strip
        self.max_frames = int(max_frames)
        self.vpm_scale = int(vpm_scale)
        self.strip_h = int(strip_h)
        self.bg = tuple(bg) if isinstance(bg, (list, tuple)) else (10, 10, 12)
        self.default_fps = int(fps) if fps is not None else 6  # default 6 if not provided

    def add_frame(self, vpm_uint8: np.ndarray, metrics: dict):
        """
        vpm_uint8: HxWx3 (uint8) — small VPM or tile at this timestep
        metrics:   {"step": int, "loss": float, "val_loss": float, "acc": float, "alerts": dict}
        """
        if len(self.frames) >= self.max_frames:
            return
        self.frames.append(vpm_uint8.copy())
        self.meta.append(
            {
            "t": time.time(),
            "step": metrics.get("step", len(self.frames) - 1),
            "loss": float(metrics.get("loss", np.nan)),
            "val_loss": float(metrics.get("val_loss", np.nan)),
            "acc": float(metrics.get("acc", np.nan)),
            "alerts": dict(metrics.get("alerts", {})),
            }
        )

    def _compose_panel(self, vpm: np.ndarray, hist: list) -> Image.Image:
        """
        Build one composite frame:
        - top: scaled VPM (nearest)
        - bottom: metric mini-timeline (last K points)
        """
        # --- top: scale the VPM ---
        H, W, _ = vpm.shape
        scale = self.vpm_scale
        top = Image.fromarray(vpm).resize(
            (W * scale, H * scale), resample=Image.NEAREST
        )

        # --- bottom: timeline strip ---
        K = min(300, len(hist))
        tail = hist[-K:]
        strip_w = top.width
        strip = Image.new("RGB", (strip_w, self.strip_h), self.bg)
        draw = ImageDraw.Draw(strip)

        # Normalize and plot tiny sparklines
        def norm(series):
            arr = np.array(series, dtype=np.float32)
            good = np.isfinite(arr)
            if good.sum() < 2:  # fallback
                return np.zeros_like(arr)
            a = arr[good]
            lo, hi = np.percentile(a, 5), np.percentile(a, 95)
            if hi - lo < 1e-8:
                hi = lo + 1e-8
            arr = np.clip((arr - lo) / (hi - lo), 0, 1)
            arr[~good] = np.nan
            return arr

        losses = norm([d["loss"] for d in tail])
        vlosses = norm([d["val_loss"] for d in tail])
        accs = norm([d["acc"] for d in tail])

        # helper to draw one sparkline
        def draw_line(vals, y0, color):
            if len(vals) < 2:
                return
            w = strip_w
            xs = np.linspace(0, w - 1, num=len(vals))
            pts = []
            for x, v in zip(xs, vals):
                if np.isnan(v):
                    continue
                y = int(y0 + (1.0 - v) * (self.strip_h / 3 - 6))
                pts.append((int(x), y))
            if len(pts) > 1:
                draw.line(pts, fill=color, width=1)

        # three stacked sparklines
        h3 = self.strip_h // 3
        draw_line(losses, 1 + 0 * h3, (200, 120, 120))  # loss
        draw_line(vlosses, 1 + 1 * h3, (120, 180, 220))  # val_loss
        draw_line(accs, 1 + 2 * h3, (140, 220, 140))  # acc

        # alert ticks (e.g., overfit) across bottom
        for i, d in enumerate(tail):
            x = int(i * (strip_w - 1) / max(1, K - 1))
            alerts = d["alerts"]
            if alerts.get("overfit", False):
                draw.line(
                    [(x, self.strip_h - 6), (x, self.strip_h - 1)],
                    fill=(255, 80, 80),
                    width=1,
                )
            if alerts.get("drift", False):
                draw.line(
                    [(x, self.strip_h - 12), (x, self.strip_h - 7)],
                    fill=(255, 200, 80),
                    width=1,
                )

        # --- stack top + bottom ---
        panel = Image.new("RGB", (top.width, top.height + strip.height), self.bg)
        panel.paste(top, (0, 0))
        panel.paste(strip, (0, top.height))
        return panel

    def save_gif(
        self,
        path: str = "training_heartbeat.gif",
        fps: int | None = None,
        optimize: bool = True,
        loop: int = 0,
        use_palette: bool = True,
        context: dict | None = None,
    ):
        """
        Save accumulated frames to an animated GIF.
        If fps is None, uses the fps provided at construction (default_fps).
        Args:
            path: Output file path.
            fps: Frames per second.
            optimize: Whether to optimize GIF size.
            loop: Number of loops (0 = infinite).
            use_palette: If True, quantize to 256-color palette (smaller, lossy).
                        If False, keep RGB frames (bigger, lossless).
        """

        if not self.frames:
            raise RuntimeError("No frames added.")

        # Compose panels (stride decimation if too many frames)
        panels = []
        stride = max(1, len(self.frames) // self.max_frames)
        for i in range(0, len(self.frames), stride):
            panels.append(self._compose_panel(self.frames[i], self.meta[: i + 1]))

        # Auto override: analysis mode forces RGB
        if context and context.get("enable_analysis", False):
            use_palette = False

        if use_palette:
            # Convert to palette (lossy, but smaller)
            frames_out = [im.convert("P", palette=Image.ADAPTIVE, colors=256) for im in panels]
        else:
            # Keep RGB (full fidelity, bigger file)
            frames_out = [im.convert("RGB") for im in panels]

        eff_fps = int(self.default_fps if fps is None else fps)
        duration_ms = int(1000 / max(1, eff_fps))

        # Pillow's GIF writer supports optimize/disposal; keep them.
        frames_out[0].save(
            path,
            save_all=True,
            append_images=frames_out[1:],
            duration=duration_ms,
            loop=loop,
            optimize=optimize,
            disposal=2,
        )
        return path
