"""Fill locked prompt slots. Never free-form extra prompt text."""

from __future__ import annotations

DESCRIPTION = "[ICON_DESCRIPTION]"
COLOR = "[COLOR]"
MATERIAL = "[MATERIAL_AND_EFFECT]"
NEON_GLOW = "neon glow"


def fill_template(template: str, description: str, color: str, material: str) -> str:
    """Replace the three catalog slots only."""
    filled = (
        template.replace(DESCRIPTION, description).replace(COLOR, color).replace(MATERIAL, material)
    )
    return filled.strip() + "\n"


def negative_for_effect(negative: str, effect: str) -> str:
    """Drop the neon-glow token for neon so emission is not suppressed."""
    text = negative.strip()
    if effect != "neon":
        return text
    parts = [part.strip() for part in text.split(",")]
    kept = [part for part in parts if part.lower() != NEON_GLOW]
    return ", ".join(kept)
