"""Load and schema-validate catalog/icons.yaml."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
_WEIGHT_MIN = 0.7
_WEIGHT_MAX = 0.85


@dataclass(frozen=True)
class ControlNet:
    type: str
    weight: float


@dataclass(frozen=True)
class Pack:
    name: str
    camera: str
    backdrop: str
    resolution: int
    controlnet: ControlNet
    seed_strategy: str


@dataclass(frozen=True)
class Icon:
    id: str
    source: str
    description: str
    color: str
    effects: dict[str, str]


@dataclass(frozen=True)
class Catalog:
    pack: Pack
    icons: tuple[Icon, ...]


class CatalogError(ValueError):
    """Invalid catalog or missing source file."""


def _req(data: dict[str, Any], key: str, ctx: str) -> Any:
    if key not in data:
        raise CatalogError(f"{ctx} missing '{key}'")
    return data[key]


def _pack(raw: dict[str, Any]) -> Pack:
    cn_raw = _req(raw, "controlnet", "pack")
    if not isinstance(cn_raw, dict):
        raise CatalogError("pack.controlnet must be a mapping")
    weight = float(_req(cn_raw, "weight", "pack.controlnet"))
    if not _WEIGHT_MIN <= weight <= _WEIGHT_MAX:
        raise CatalogError(f"controlnet.weight must be {_WEIGHT_MIN}-{_WEIGHT_MAX}")
    return Pack(
        name=str(_req(raw, "name", "pack")),
        camera=str(_req(raw, "camera", "pack")),
        backdrop=str(_req(raw, "backdrop", "pack")),
        resolution=int(_req(raw, "resolution", "pack")),
        controlnet=ControlNet(type=str(_req(cn_raw, "type", "pack.controlnet")), weight=weight),
        seed_strategy=str(_req(raw, "seed_strategy", "pack")),
    )


def _icon(raw: dict[str, Any]) -> Icon:
    icon_id = str(_req(raw, "id", "icon"))
    color = str(_req(raw, "color", icon_id))
    if not _COLOR.match(color):
        raise CatalogError(f"{icon_id} color must be #RRGGBB")
    effects_raw = _req(raw, "effects", icon_id)
    if not isinstance(effects_raw, dict) or not effects_raw:
        raise CatalogError(f"{icon_id} needs effects")
    effects: dict[str, str] = {}
    for name, body in effects_raw.items():
        if not isinstance(body, dict) or "material" not in body:
            raise CatalogError(f"{icon_id}.{name} needs material")
        effects[str(name)] = str(body["material"])
    if "tame" not in effects or "neon" not in effects:
        raise CatalogError(f"{icon_id} must define tame and neon effects")
    return Icon(
        id=icon_id,
        source=str(_req(raw, "source", icon_id)),
        description=str(_req(raw, "description", icon_id)),
        color=color,
        effects=effects,
    )


def load_catalog(path: Path, *, root: Path | None = None) -> Catalog:
    """Parse YAML and require every source file to exist under root."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CatalogError("catalog root must be a mapping")
    pack = _pack(_req(data, "pack", "catalog"))
    icons_raw = _req(data, "icons", "catalog")
    if not isinstance(icons_raw, list) or not icons_raw:
        raise CatalogError("icons must be a non-empty list")
    icons_list: list[Icon] = []
    for item in icons_raw:
        if not isinstance(item, dict):
            raise CatalogError("icon must be a mapping")
        icons_list.append(_icon(item))
    base = root or path.parent.parent
    for icon in icons_list:
        source = base / icon.source
        if not source.is_file():
            raise CatalogError(f"{icon.id} source missing: {icon.source}")
    return Catalog(pack=pack, icons=tuple(icons_list))
