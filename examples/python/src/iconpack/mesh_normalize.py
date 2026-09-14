"""CPU helpers for SVG viewBox scale (Blender uses the same numbers)."""

from __future__ import annotations

import re
from xml.etree import ElementTree

_VIEWBOX = re.compile(
    r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)"
)
TARGET = 2.0
PAD_FRACTION = 0.22


def viewbox_size(svg_text: str) -> tuple[float, float]:
    """Return width, height from viewBox or width/height attributes."""
    root = ElementTree.fromstring(svg_text)
    vb = root.attrib.get("viewBox") or root.attrib.get("viewbox")
    if vb:
        match = _VIEWBOX.search(vb)
        if match:
            width = float(match.group(3))
            height = float(match.group(4))
            if width > 0 and height > 0:
                return width, height
    width = float(root.attrib.get("width", "256").replace("px", ""))
    height = float(root.attrib.get("height", "256").replace("px", ""))
    return width, height


def normalize_scale(width: float, height: float, *, target: float = TARGET) -> float:
    """Scale so the longest side equals target (unit-ish object)."""
    longest = max(width, height)
    if longest <= 0:
        raise ValueError("SVG viewBox must be positive")
    return target / longest


def padded_camera_distance(*, pad_fraction: float = PAD_FRACTION) -> float:
    """Keep ~18-25% inset around a unit object for adaptive-icon masks."""
    if not 0.18 <= pad_fraction <= 0.25:
        raise ValueError("pad_fraction must be 0.18-0.25")
    return 1.0 / (1.0 - 2.0 * pad_fraction)
