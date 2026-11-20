"""Render a 3D model as a clean product shot on a transparent background, for the page's "made thing".

    blender -b -P studio-render.py -- --model product.glb --out hero.png [--res 1600] [--turn 30] [--tilt 12]
                                      [--samples 96] [--lens 85] [--tint FF4A12]

Takes .glb/.gltf, .obj, .fbx, .stl, .ply or a .blend to append. The model is centred and framed automatically, lit by
a soft key, a rim and a low fill, and rendered with Cycles on the CPU (no GPU needed). --turn spins it about the
vertical axis, --tilt raises the camera. --tint paints everything one colour (useful for an untextured .stl).
Blender 4.2 or newer. A 1600 px still takes roughly one to five minutes on four cores.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
arg = lambda k, d=None: argv[argv.index('--' + k) + 1] if '--' + k in argv else d
model, out = arg('model'), arg('out', 'render.png')
if not model or not os.path.exists(model):
    sys.exit('give a model:  blender -b -P studio-render.py -- --model product.glb --out hero.png')

bpy.ops.wm.read_factory_settings(use_empty=True)
ext = os.path.splitext(model)[1].lower()
if ext in ('.glb', '.gltf'):
    bpy.ops.import_scene.gltf(filepath=model)
elif ext == '.obj':
    bpy.ops.wm.obj_import(filepath=model)
elif ext == '.fbx':
    bpy.ops.import_scene.fbx(filepath=model)
elif ext == '.stl':
    bpy.ops.wm.stl_import(filepath=model)
elif ext == '.ply':
    bpy.ops.wm.ply_import(filepath=model)
elif ext == '.blend':
    with bpy.data.libraries.load(model) as (src, dst):
        dst.objects = src.objects
    for o in dst.objects:
        if o:
            bpy.context.scene.collection.objects.link(o)
else:
    sys.exit('unsupported model type: ' + ext)

sc = bpy.context.scene
meshes = [o for o in sc.objects if o.type == 'MESH']
if not meshes:
    sys.exit('no meshes in ' + model)
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
centre, radius = (lo + hi) / 2, max((hi - lo).length / 2, 1e-6)

if arg('tint'):
    h = arg('tint').lstrip('#')
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    m = bpy.data.materials.new('Tint')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value, b.inputs['Roughness'].default_value = (*lin, 1), 0.4
    for o in meshes:
        o.data.materials.clear()
        o.data.materials.append(m)

# camera: looking at the centre from the front, turned and raised
turn, tilt = math.radians(float(arg('turn', 30))), math.radians(float(arg('tilt', 12)))
cam = bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))
cam.data.lens = float(arg('lens', 85))
direction = Vector((math.sin(turn) * math.cos(tilt), -math.cos(turn) * math.cos(tilt), math.sin(tilt)))
side = Vector((math.cos(turn), math.sin(turn), 0))
above = direction.cross(side)
half = 18 / cam.data.lens * 0.88                                        # half the frame, as a slope, with a margin
dist = max(max(abs((p - centre).dot(side)), abs((p - centre).dot(above))) / half + (p - centre).dot(direction) for p in pts)
cam.location = centre + direction * dist
cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.clip_start, cam.data.clip_end = dist / 100, dist * 10
sc.collection.objects.link(cam)
sc.camera = cam


def area(name, offset, size, power, colour=(1, 1, 1)):
    """A soft panel light, placed relative to the camera's view: (right, up, toward camera) in model radii."""
    right = Vector((math.cos(turn), math.sin(turn), 0))
    up = Vector((0, 0, 1))
    d = bpy.data.lights.new(name, 'AREA')
    d.shape, d.size, d.size_y, d.color = 'RECTANGLE', size[0] * radius, size[1] * radius, colour
    d.energy = power * radius * radius
    o = bpy.data.objects.new(name, d)
    o.location = centre + (right * offset[0] + up * offset[1] + direction * offset[2]) * radius
    o.rotation_euler = (centre - o.location).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(o)


area('Key', (-2.6, 3.0, 2.6), (3.2, 3.2), 190, (1.0, 0.97, 0.93))
area('Rim', (3.2, 1.6, -2.4), (0.8, 4.0), 120, (0.94, 0.97, 1.0))
area('Fill', (1.5, -2.0, 2.4), (4.0, 2.4), 28, (1.0, 0.95, 0.9))
world = bpy.data.worlds.new('World')
sc.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.87, 0.82, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.25

sc.render.engine = 'CYCLES'
sc.cycles.device, sc.cycles.samples = 'CPU', int(arg('samples', 96))
sc.cycles.use_adaptive_sampling, sc.cycles.adaptive_threshold, sc.cycles.use_denoising = True, 0.02, True
sc.render.resolution_x = sc.render.resolution_y = int(arg('res', 1600))
sc.render.film_transparent = True
sc.render.image_settings.file_format, sc.render.image_settings.color_mode = 'PNG', 'RGBA'
sc.view_settings.view_transform, sc.view_settings.look = 'Standard', 'None'
sc.render.filepath = os.path.abspath(out)
bpy.ops.render.render(write_still=True)
print('wrote', sc.render.filepath)
