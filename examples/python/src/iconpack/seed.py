"""Stable 32-bit seeds from icon id + effect name."""

from __future__ import annotations

import hashlib

_MOD = 2**31


def seed_for(icon_id: str, effect: str) -> int:
    """Return sha256(icon_id:effect) as a positive 31-bit integer."""
    digest = hashlib.sha256(f"{icon_id}:{effect}".encode()).digest()
    return int.from_bytes(digest[:4], "big") % _MOD
