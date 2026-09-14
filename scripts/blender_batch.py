#!/usr/bin/env python3
# Runs inside Blender. Builds one locked studio shot from a job JSON.
"""Locked Hover Icons scene: 15-degree three-quarter, 45-degree key, 1024 PNG.

Contrast is king: icons must stay glanceable. Neon is an edge tube only.
"""

from __future__ import annotations

import colorsys
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

GRAY = (0.06, 0.06, 0.07, 1.0)
FLOOR = (0.06, 0.06, 0.07, 1.0)
HOVER_GAP = 0.08
FRAME_WIDTH = 1.55
FRAME_HEIGHT = 1.55
TUBE_RADIUS = 0.08
TUBE_RADIUS_MAX_FRAC = 0.22
TUBE_SEGMENTS = 8
# Apple Big Sur / product-icon lock: upright object, 15° look-down,
# 30° right three-quarter (front + right side; faces slightly left).
ICON_STAND = math.radians(90)
ICON_YAW = 0.0
THREE_QUARTER = math.radians(30)
CAM_AZIMUTH = math.atan2(math.sin(THREE_QUARTER), -math.cos(THREE_QUARTER))
CAM_ELEVATION = math.radians(15)
CAM_DIST = 5.85


def _argv_job() -> Path:
    if "--" not in sys.argv:
        raise SystemExit("What failed: missing -- job.json for blender_batch.py")
    return Path(sys.argv[sys.argv.index("--") + 1])


def _hex_rgba(color: str) -> tuple[float, float, float, float]:
    raw = color.lstrip("#")
    return tuple(int(raw[i : i + 2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)


def _emit_rgba(color: str) -> tuple[float, float, float, float]:
    """Neon gas: dark rich catalog hue. Low value so the tube stays blue, not pale."""
    r, g, b, a = _hex_rgba(color)
    avg = (r + g + b) / 3.0
    chroma = max(abs(r - avg), abs(g - avg), abs(b - avg))
    if chroma < 0.04:
        tone = min(0.20, max(avg, 0.14))
        return (tone, tone, tone, a)
    h, _s, _v = colorsys.rgb_to_hsv(r, g, b)
    if 0.50 <= h <= 0.70:
        h = 0.68
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 0.32)
    peak = max(r, g, b, 1e-6)
    r = r if r >= peak * 0.9 else r * 0.04
    g = g if g >= peak * 0.9 else g * 0.05
    b = b if b >= peak * 0.9 else b * 0.04
    return (r, g, b, a)


def _body_rgba(color: str) -> tuple[float, float, float, float]:
    """Dark saturated satin under the tube so the icon does not wash out."""
    r, g, b, a = _hex_rgba(color)
    avg = (r + g + b) / 3.0
    chroma = max(abs(r - avg), abs(g - avg), abs(b - avg))
    if chroma < 0.04:
        tone = min(0.10, max(avg * 0.45, 0.06))
        return (tone, tone, tone, a)
    h, _s, _v = colorsys.rgb_to_hsv(r, g, b)
    if 0.50 <= h <= 0.70:
        h = 0.68
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 0.14)
    return (r, g, b, a)


def _reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.preferences.addon_enable(module="io_curve_svg")
    except Exception:
        pass


def _enable_gpu(scene: bpy.types.Scene, requested: str) -> str:
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    order = [requested.upper(), "CUDA"] if requested.upper() != "CUDA" else ["CUDA"]
    for device_type in order:
        try:
            prefs.compute_device_type = device_type
            prefs.get_devices()
        except Exception:
            continue
        devices = getattr(prefs, "devices", [])
        gpu = False
        for device in devices:
            is_gpu = "CPU" not in device.type
            device.use = is_gpu
            gpu = gpu or is_gpu
        if gpu:
            return device_type
    raise SystemExit(
        "What failed: no OptiX/CUDA Cycles device\n"
        "What to run: official Blender tarball + NVIDIA driver; set CYCLES_DEVICE\n"
        "Why: CPU Cycles is not an allowed silent fallback"
    )


def _world_and_lights(effect: str) -> None:
    world = bpy.data.worlds.new("Studio")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = GRAY
    bg.inputs[1].default_value = 0.18
    neon = effect == "neon"

    def area(name: str, loc: tuple[float, float, float], energy: float, size: float) -> None:
        light = bpy.data.lights.new(name, "AREA")
        light.energy = energy
        light.size = size
        obj = bpy.data.objects.new(name, light)
        obj.location = loc
        bpy.context.scene.collection.objects.link(obj)
        obj.rotation_euler = (math.radians(-45), 0.0, math.atan2(loc[0], max(loc[1], 0.01)))

    area("Key", (-2.8, -2.2, 3.8), 520.0 if neon else 420.0, 1.7 if neon else 2.4)
    area("Fill", (2.8, 1.6, 2.0), 52.0 if neon else 42.0, 3.2)
    area("Rim", (0.15, 3.4, 2.6), 180.0 if neon else 90.0, 1.1 if neon else 1.4)


def _look_target() -> bpy.types.Object:
    obj = bpy.data.objects.new("LookAt", None)
    obj.location = (0.0, 0.0, HOVER_GAP + FRAME_HEIGHT * 0.5)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _camera(target: bpy.types.Object) -> None:
    cam = bpy.data.cameras.new("IconCam")
    cam.lens = 85
    obj = bpy.data.objects.new("IconCam", cam)
    horizontal = CAM_DIST * math.cos(CAM_ELEVATION)
    obj.location = (
        target.location.x + horizontal * math.sin(CAM_AZIMUTH),
        target.location.y + horizontal * math.cos(CAM_AZIMUTH),
        target.location.z + CAM_DIST * math.sin(CAM_ELEVATION),
    )
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.scene.camera = obj
    track = obj.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"


def _studio_mat() -> bpy.types.Material:
    mat = bpy.data.materials.new("StudioSurf")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = FLOOR
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.45
    return mat


def _shadow_plane() -> None:
    mat = _studio_mat()
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0.0))
    floor = bpy.context.object
    floor.data.materials.append(mat)
    bpy.ops.mesh.primitive_plane_add(
        size=16,
        location=(0.0, 4.4, 3.6),
        rotation=(math.radians(86), 0.0, 0.0),
    )
    bpy.context.object.data.materials.append(mat)


def _link_imported(imported: list[bpy.types.Object]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    for obj in imported:
        if obj.name not in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.link(obj)
        if obj.type == "CURVE" and obj.data:
            obj.data.dimensions = "3D"
        parts.append(obj)
    if not parts:
        raise SystemExit("What failed: SVG import produced no meshes")
    return parts


def _world_aabb(objs: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    bpy.context.view_layer.update()
    low = Vector((1e9, 1e9, 1e9))
    high = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        matrix = obj.matrix_world
        for corner in obj.bound_box:
            world = matrix @ Vector(corner)
            low.x, low.y, low.z = min(low.x, world.x), min(low.y, world.y), min(low.z, world.z)
            high.x, high.y, high.z = (
                max(high.x, world.x),
                max(high.y, world.y),
                max(high.z, world.z),
            )
    return low, high


def _reset_curve_radii(data: bpy.types.Curve) -> float:
    """Apply-scale multiplies point radius; reset so bevel_depth stays in scene units."""
    xs: list[float] = []
    ys: list[float] = []
    for spline in data.splines:
        for point in (*spline.bezier_points, *spline.points):
            point.radius = 1.0
            xs.append(point.co.x)
            ys.append(point.co.y)
    if not xs:
        return 2.0
    return max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)


def _apply_tubes(obj: bpy.types.Object) -> bpy.types.Object:
    """Round tube along the SVG outline; the interior stays empty."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if obj.type == "CURVE" and obj.data:
        data = obj.data
        data.dimensions = "3D"
        data.extrude = 0.0
        span = _reset_curve_radii(data)
        data.bevel_depth = min(TUBE_RADIUS, span * TUBE_RADIUS_MAX_FRAC)
        data.bevel_resolution = TUBE_SEGMENTS
        if hasattr(data, "use_fill_caps"):
            data.use_fill_caps = True
        if hasattr(data, "fill_mode"):
            data.fill_mode = "FULL"
    bpy.ops.object.convert(target="MESH")
    mesh = bpy.context.view_layer.objects.active
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0008)
    bmesh.ops.dissolve_degenerate(bm, dist=0.0008, edges=list(bm.edges))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh.data)
    bm.free()
    for poly in mesh.data.polygons:
        poly.use_smooth = True
    return mesh


def _mesh_children(root: bpy.types.Object) -> list[bpy.types.Object]:
    return [child for child in root.children if child.type == "MESH"]


def _fit_in_frame(root: bpy.types.Object) -> None:
    """Uniform-scale posed meshes into a locked box, then center on the box origin."""
    bpy.context.view_layer.update()
    parts = _mesh_children(root)
    if not parts:
        return
    low, high = _world_aabb(parts)
    size = high - low
    span_w = max(size.x, 1e-9)
    span_h = max(size.z, 1e-9)
    scale = min(FRAME_WIDTH / span_w, FRAME_HEIGHT / span_h)
    root.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    low, high = _world_aabb(parts)
    mid = (low + high) * 0.5
    root.location.x += -mid.x
    root.location.y += -mid.y
    root.location.z += (HOVER_GAP + FRAME_HEIGHT * 0.5) - mid.z
    bpy.context.view_layer.update()
    low, high = _world_aabb(parts)
    size = high - low
    print(f"icon loc={tuple(root.location)} size=({size.x:.3f},{size.y:.3f},{size.z:.3f})")


def _import_svg(svg: Path) -> bpy.types.Object:
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=str(svg))
    imported = [
        obj
        for obj in bpy.data.objects
        if obj not in before and obj.type in {"CURVE", "MESH"}
    ]
    if not imported:
        raise SystemExit(f"What failed: SVG import produced no objects ({svg})")
    parts = _link_imported(imported)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.context.view_layer.update()
    low, high = _world_aabb(parts)
    center = (low + high) * 0.5
    bpy.context.scene.cursor.location = center
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    longest = max(high.x - low.x, high.y - low.y, 1e-9)
    scale = 2.0 / longest
    for obj in parts:
        obj.scale = (scale, scale, scale)
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    meshes = [_apply_tubes(obj) for obj in parts]
    ranked = sorted(meshes, key=lambda o: o.dimensions.x * o.dimensions.y)
    for obj in ranked[:-1]:
        obj.location.z += 0.05
    root = bpy.data.objects.new("IconRoot", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in meshes:
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (ICON_STAND, 0.0, ICON_YAW)
    _fit_in_frame(root)
    print(f"icon parts={len(meshes)}")
    return root


def _set_input(bsdf: bpy.types.Node, name: str, value: float, fallback: str | None = None) -> None:
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = value
    elif fallback and fallback in bsdf.inputs:
        bsdf.inputs[fallback].default_value = value


def _neon_tube(mat: bpy.types.Material, color: str) -> None:
    """Glow on top of satin so the cylinder still shows highlights and bounce."""
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    out = nodes["Material Output"]
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = _emit_rgba(color)
    rgba = _hex_rgba(color)
    avg = (rgba[0] + rgba[1] + rgba[2]) / 3.0
    chroma = max(abs(rgba[0] - avg), abs(rgba[1] - avg), abs(rgba[2] - avg))
    emit.inputs["Strength"].default_value = 5.0 if chroma < 0.04 else 14.0
    mix = nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.38
    links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    links.new(emit.outputs["Emission"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])


def _material(root: bpy.types.Object, color: str, effect: str) -> None:
    known = ("tame", "neon", "glass", "metal", "ceramic")
    if effect not in known:
        raise RuntimeError(f"unknown effect {effect!r}; expected {known}")
    mat = bpy.data.materials.new("IconMat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    rgba = _hex_rgba(color)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.12
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.0
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.5
        bsdf.inputs["Coat Roughness"].default_value = 0.06
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = 0.35
    if effect == "glass":
        bsdf.inputs["Roughness"].default_value = 0.04
        _set_input(bsdf, "Metallic", 0.0)
        _set_input(bsdf, "Transmission Weight", 1.0, "Transmission")
        _set_input(bsdf, "IOR", 1.45)
    elif effect == "metal":
        bsdf.inputs["Roughness"].default_value = 0.12
        _set_input(bsdf, "Metallic", 1.0)
        _set_input(bsdf, "Transmission Weight", 0.0, "Transmission")
    elif effect == "ceramic":
        bsdf.inputs["Roughness"].default_value = 0.42
        _set_input(bsdf, "Metallic", 0.0)
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.55
    if effect == "neon":
        bsdf.inputs["Base Color"].default_value = _body_rgba(color)
        bsdf.inputs["Roughness"].default_value = 0.10
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.55
            bsdf.inputs["Coat Roughness"].default_value = 0.05
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.5
        _neon_tube(mat, color)
    targets = [root] if root.type == "MESH" else list(root.children)
    for obj in targets:
        if obj.type != "MESH":
            continue
        obj.data.materials.clear()
        obj.data.materials.append(mat)


def _glare(scene: bpy.types.Scene, effect: str, color: str) -> None:
    """Colored fog glow: saturate the bloom so it stays gas-colored, never white."""
    scene.use_nodes = True
    tree = scene.node_tree
    links = tree.links
    tree.nodes.clear()
    src = tree.nodes.new("CompositorNodeRLayers")
    composite = tree.nodes.new("CompositorNodeComposite")
    last = src.outputs["Image"]
    if effect == "neon":
        rgba = _hex_rgba(color)
        avg = (rgba[0] + rgba[1] + rgba[2]) / 3.0
        chroma = max(abs(rgba[0] - avg), abs(rgba[1] - avg), abs(rgba[2] - avg))
        glare = tree.nodes.new("CompositorNodeGlare")
        glare.glare_type = "FOG_GLOW"
        if hasattr(glare, "mix"):
            glare.mix = -0.12 if chroma >= 0.04 else -0.55
        if "Saturation" in glare.inputs:
            glare.inputs["Saturation"].default_value = 4.5 if chroma >= 0.04 else 1.0
        if "Tint" in glare.inputs:
            glare.inputs["Tint"].default_value = _emit_rgba(color)
        if "Strength" in glare.inputs:
            glare.inputs["Strength"].default_value = 1.15 if chroma >= 0.04 else 0.55
        if "Threshold" in glare.inputs:
            glare.inputs["Threshold"].default_value = 0.14
        elif hasattr(glare, "threshold"):
            glare.threshold = 0.14
        if "Size" in glare.inputs:
            glare.inputs["Size"].default_value = 0.72
        sat = tree.nodes.new("CompositorNodeHueSat")
        sat.inputs["Saturation"].default_value = 2.2 if chroma >= 0.04 else 1.0
        sat.inputs["Value"].default_value = 0.95 if chroma >= 0.04 else 0.72
        add = tree.nodes.new("CompositorNodeMixRGB")
        add.blend_type = "ADD"
        add.inputs["Fac"].default_value = 0.55 if chroma >= 0.04 else 0.28
        links.new(src.outputs["Image"], glare.inputs["Image"])
        glow = glare.outputs["Glare"] if "Glare" in glare.outputs else glare.outputs["Image"]
        links.new(glow, sat.inputs["Image"])
        links.new(src.outputs["Image"], add.inputs[1])
        links.new(sat.outputs["Image"], add.inputs[2])
        last = add.outputs["Image"]
    links.new(last, composite.inputs["Image"])


def _render(job: dict, quality: str, device: str) -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = int(job["resolution"])
    scene.render.resolution_y = int(job["resolution"])
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(Path(job["root"]) / job["png_path"])
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = "AgX"
        look = "AgX - Punchy" if job.get("effect") == "neon" else "AgX - Base Contrast"
        scene.view_settings.look = look
        scene.view_settings.exposure = 0.05 if job.get("effect") == "neon" else 0.15
    except TypeError:
        pass
    Path(scene.render.filepath).parent.mkdir(parents=True, exist_ok=True)
    if quality == "draft":
        for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                scene.render.engine = engine
                break
            except TypeError:
                continue
        bpy.ops.render.render(write_still=True)
        return
    used = _enable_gpu(scene, device)
    scene.cycles.samples = 96
    scene.cycles.max_bounces = 12
    scene.cycles.diffuse_bounces = 8
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPTIX" if used == "OPTIX" else "OPENIMAGEDENOISE"
    except TypeError:
        pass
    bpy.ops.render.render(write_still=True)


def main() -> None:
    job_path = _argv_job()
    job = json.loads(job_path.read_text(encoding="utf-8"))
    root = Path(job["root"])
    _reset_scene()
    _world_and_lights(job["effect"])
    _shadow_plane()
    icon = _import_svg(root / job["source"])
    _camera(_look_target())
    _material(icon, job["color"], job["effect"])
    mesh_path = root / job["mesh_path"]
    mesh_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    icon.select_set(True)
    for child in icon.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = icon
    bpy.ops.export_scene.gltf(filepath=str(mesh_path), use_selection=True)
    _glare(bpy.context.scene, job["effect"], job["color"])
    _render(job, job.get("quality", "release"), job.get("cycles_device", "OPTIX"))
    png = root / job["png_path"]
    golden = root / job["golden_path"]
    if png.is_file():
        golden.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png, golden)
    sidecar = root / job["json_path"]
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    job["blender"] = bpy.app.version_string
    sidecar.write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"What failed: blender_batch {exc}", file=sys.stderr)
        sys.exit(1)
