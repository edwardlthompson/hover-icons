"""Blender material presets for extra catalog effects."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = (ROOT / "scripts" / "blender_batch.py").read_text(encoding="utf-8")


class BlenderPresetTests(unittest.TestCase):
    def test_named_presets_and_unknown_guard(self) -> None:
        for name in ("glass", "metal", "ceramic"):
            self.assertIn(f'effect == "{name}"', BATCH)
        self.assertIn("unknown effect", BATCH)
        self.assertIn("HOVER_GAP = 0.08", BATCH)
        self.assertIn("FRAME_WIDTH = 1.55", BATCH)
        self.assertIn("FRAME_HEIGHT = 1.55", BATCH)
        self.assertIn("_fit_in_frame", BATCH)
        self.assertIn("HOVER_GAP + FRAME_HEIGHT * 0.5", BATCH)
        self.assertIn("CAM_ELEVATION = math.radians(15)", BATCH)
        self.assertIn("THREE_QUARTER = math.radians(30)", BATCH)
        self.assertIn("ICON_STAND = math.radians(90)", BATCH)
        self.assertIn("ICON_YAW = 0.0", BATCH)
        self.assertIn('GRAY = (0.06, 0.06, 0.07, 1.0)', BATCH)
        self.assertIn("bg.inputs[1].default_value = 0.18", BATCH)
        self.assertIn("LookAt", BATCH)
        self.assertIn("Emission Strength", BATCH)
        self.assertIn("_neon_tube", BATCH)
        self.assertIn("Contrast is king", BATCH)
        self.assertIn("ShaderNodeEmission", BATCH)
        self.assertIn("AgX - Base Contrast", BATCH)
        self.assertIn("Transmission Weight", BATCH)
        self.assertIn("Metallic", BATCH)
        self.assertIn('bsdf.inputs["Roughness"].default_value = 0.22', BATCH)
        self.assertIn("TUBE_RADIUS = 0.08", BATCH)
        self.assertIn("TUBE_RADIUS_MAX_FRAC = 0.22", BATCH)
        self.assertIn("point.radius = 1.0", BATCH)
        self.assertIn('data.dimensions = "3D"', BATCH)
        self.assertIn("bevel_depth = min(TUBE_RADIUS", BATCH)
        self.assertIn('_apply_tubes', BATCH)
        self.assertIn('mix.inputs["Fac"].default_value = 0.38', BATCH)
        self.assertIn("poly.use_smooth = True", BATCH)
        self.assertIn("chroma < 0.04", BATCH)
        self.assertIn("hsv_to_rgb", BATCH)
        self.assertIn("h = 0.68", BATCH)
        self.assertIn("1.0, 0.32", BATCH)
        self.assertIn("_body_rgba", BATCH)
        self.assertIn("5.0 if chroma < 0.04 else 14.0", BATCH)
        self.assertIn("520.0 if neon else 420.0", BATCH)
        self.assertIn("CompositorNodeGlare", BATCH)
        self.assertIn("CompositorNodeHueSat", BATCH)
        self.assertIn('blend_type = "ADD"', BATCH)
        self.assertIn('add.inputs["Fac"].default_value = 0.55 if chroma >= 0.04 else 0.28', BATCH)
        self.assertIn("Saturation", BATCH)
        self.assertIn("ShaderNodeMixShader", BATCH)
        self.assertIn("AgX - Punchy", BATCH)
        self.assertNotIn("ShaderNodeAddShader", BATCH)
        self.assertNotIn("_apply_solidify", BATCH)
        self.assertNotIn("_neon_strength", BATCH)
        self.assertNotIn("0.3 / peak", BATCH)

    def test_messages_tail_is_not_degenerate(self) -> None:
        svg = (ROOT / "catalog" / "sources" / "messages.svg").read_text(encoding="utf-8")
        self.assertNotIn("L72 214", svg)
        self.assertNotIn("l-28 48", svg)
        self.assertIn("c-16 6-28 30-30 44", svg)


if __name__ == "__main__":
    unittest.main()
