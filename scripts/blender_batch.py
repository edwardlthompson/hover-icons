#!/usr/bin/env python3
# Runs inside Blender. Builds one locked studio shot from a job JSON.
"""Locked Hover Icons scene: 15-degree three-quarter, 45-degree key, 1024 PNG."""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

GRAY = (0.78, 0.78, 0.80, 1.0)


def _argv_job() -> Path:
    if "--" not in sys.argv:
        raise SystemExit("What failed: missing -- job.json for blender_batch.py")
    return Path(sys.argv[sys.argv.index("--") + 1])


def _hex_rgba(color: str) -> tuple[float, float, float, float]:
    raw = color.lstrip("#")
    return tuple(int(raw[i : i + 2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)


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


def _world_and_lights() -> None:
    world = bpy.data.worlds.new("Studio")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = GRAY
    bg.inputs[1].default_value = 1.0

    def area(name: str, loc: tuple[float, float, float], energy: float, size: float) -> None:
        light = bpy.data.lights.new(name, "AREA")
        light.energy = energy
        light.size = size
        obj = bpy.data.objects.new(name, light)
        obj.location = loc
        bpy.context.scene.collection.objects.link(obj)
        obj.rotation_euler = (math.radians(-45), 0.0, math.atan2(loc[0], max(loc[1], 0.01)))

    area("Key", (-2.8, -2.2, 3.6), 650.0, 2.4)
    area("Fill", (2.6, 1.4, 2.2), 90.0, 3.0)
    area("Rim", (0.2, 3.2, 2.4), 140.0, 1.6)


def _camera(target: bpy.types.Object) -> None:
    cam = bpy.data.cameras.new("IconCam")
    cam.lens = 85
    obj = bpy.data.objects.new("IconCam", cam)
    obj.location = (2.4, -4.6, 1.8)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.scene.camera = obj
    track = obj.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"


def _shadow_plane() -> None:
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0.0))
    plane = bpy.context.object
    mat = bpy.data.materials.new("Floor")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = GRAY
    bsdf.inputs["Roughness"].default_value = 0.85
    plane.data.materials.append(mat)


def _mesh_parts(imported: list[bpy.types.Object]) -> list[bpy.types.Object]:
    meshes: list[bpy.types.Object] = []
    for obj in imported:
        if obj.name not in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if obj.type == "CURVE" and obj.data:
            obj.data.extrude = 0.0
            obj.data.bevel_depth = 0.0
        bpy.ops.object.convert(target="MESH")
        mesh = bpy.context.view_layer.objects.active
        if mesh:
            meshes.append(mesh)
    if not meshes:
        raise SystemExit("What failed: SVG import produced no meshes")
    return meshes


def _world_aabb(meshes: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    low = Vector((1e9, 1e9, 1e9))
    high = Vector((-1e9, -1e9, -1e9))
    for obj in meshes:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            low.x, low.y, low.z = min(low.x, world.x), min(low.y, world.y), min(low.z, world.z)
            high.x, high.y, high.z = max(high.x, world.x), max(high.y, world.y), max(high.z, world.z)
    return low, high


def _apply_solidify(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    solid = obj.modifiers.new("Extrude", "SOLIDIFY")
    solid.thickness = 0.22
    solid.offset = 1.0
    bpy.ops.object.modifier_apply(modifier=solid.name)
    bevel = obj.modifiers.new("Bevel", "BEVEL")
    bevel.width = 0.018
    bevel.segments = 3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")


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
    meshes = _mesh_parts(imported)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.context.view_layer.update()
    low, high = _world_aabb(meshes)
    center = (low + high) * 0.5
    bpy.context.scene.cursor.location = center
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    longest = max(high.x - low.x, high.y - low.y, 1e-9)
    scale = 2.0 / longest
    for obj in meshes:
        obj.scale = (scale, scale, scale)
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    for obj in meshes:
        _apply_solidify(obj)
    ranked = sorted(meshes, key=lambda o: o.dimensions.x * o.dimensions.y)
    for obj in ranked[:-1]:
        obj.location.z += 0.05
    root = bpy.data.objects.new("IconRoot", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in meshes:
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
    root.location = (0.0, 0.0, 0.45)
    root.rotation_euler = (math.radians(68), 0.0, math.radians(-22))
    bpy.context.view_layer.update()
    print(f"icon parts={len(meshes)} loc={tuple(root.location)}")
    return root


def _material(root: bpy.types.Object, color: str, effect: str) -> None:
    mat = bpy.data.materials.new("IconMat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    out = nodes["Material Output"]
    rgba = _hex_rgba(color)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.18
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.35
        bsdf.inputs["Coat Roughness"].default_value = 0.08
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = 0.35
    if effect == "neon":
        emit = nodes.new("ShaderNodeEmission")
        emit.inputs["Color"].default_value = rgba
        emit.inputs["Strength"].default_value = 2.4
        layer = nodes.new("ShaderNodeLayerWeight")
        layer.inputs["Blend"].default_value = 0.22
        mix = nodes.new("ShaderNodeMixShader")
        links.new(emit.outputs["Emission"], mix.inputs[1])
        links.new(bsdf.outputs["BSDF"], mix.inputs[2])
        links.new(layer.outputs["Facing"], mix.inputs["Fac"])
        links.new(mix.outputs["Shader"], out.inputs["Surface"])
    targets = [root] if root.type == "MESH" else list(root.children)
    for obj in targets:
        if obj.type != "MESH":
            continue
        obj.data.materials.clear()
        obj.data.materials.append(mat)


def _glare(scene: bpy.types.Scene, effect: str) -> None:
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    src = tree.nodes.new("CompositorNodeRLayers")
    composite = tree.nodes.new("CompositorNodeComposite")
    last = src.outputs["Image"]
    if effect == "neon":
        glare = tree.nodes.new("CompositorNodeGlare")
        glare.glare_type = "FOG_GLOW"
        if hasattr(glare, "mix"):
            glare.mix = 0.82
        if "Strength" in glare.inputs:
            glare.inputs["Strength"].default_value = 0.25
        tree.links.new(src.outputs["Image"], glare.inputs["Image"])
        last = glare.outputs["Image"]
    tree.links.new(last, composite.inputs["Image"])


def _render(job: dict, quality: str, device: str) -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = int(job["resolution"])
    scene.render.resolution_y = int(job["resolution"])
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(Path(job["root"]) / job["png_path"])
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
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
    scene.cycles.samples = 64
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
    _world_and_lights()
    _shadow_plane()
    icon = _import_svg(root / job["source"])
    _camera(icon)
    _material(icon, job["color"], job["effect"])
    mesh_path = root / job["mesh_path"]
    mesh_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    icon.select_set(True)
    for child in icon.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = icon
    bpy.ops.export_scene.gltf(filepath=str(mesh_path), use_selection=True)
    _glare(bpy.context.scene, job["effect"])
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
