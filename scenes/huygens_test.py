# Huygens descent test shot (Titan). Procedural, headless:
#   blender -b -P scenes/huygens_test.py -- --start 1 --end 72 --out /tmp/frames --quality draft
# Scene = independent modules (terrain, haze, sky, light, probe, camera) switched by CFG,
# so later shots can reuse the engine and enable only what the subject needs.
import bpy, bmesh, sys, math
from mathutils import Vector, noise

# ---------- args ----------
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default
START = int(arg('--start', 1)); END = int(arg('--end', 72))
OUT = arg('--out', '/tmp/frames'); QUALITY = arg('--quality', 'draft'); SAMPLES = arg('--samples', None)

# ---------- config: what this shot uses ----------
CFG = dict(terrain=True, haze=True, probe=True, parachute=True, dof=True)
Q = {'draft': dict(res=(960, 540), samples=40, grid=200),
     'final': dict(res=(1920, 1080), samples=96, grid=360)}[QUALITY]
TOTAL = 72            # frames of the full shot (12 fps -> 6 s, interpolated to 24 later)
SIZE = 700.0          # terrain size in metres
random_offset = 11.7  # change per episode for a different landscape

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render ----------
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = int(SAMPLES) if SAMPLES else Q['samples']
scene.cycles.use_denoising = False   # apt Blender has no OpenImageDenoise; temporal denoise is done in ffmpeg
scene.cycles.sample_clamp_indirect = 3.0
scene.cycles.sample_clamp_direct = 20.0
scene.cycles.max_bounces = 3
scene.render.resolution_x, scene.render.resolution_y = Q['res']
scene.render.fps = 12
scene.frame_start, scene.frame_end = START, END
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT + '/f_'
scene.view_settings.view_transform = 'Filmic' if 'Filmic' in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items.keys() else 'Standard'
scene.view_settings.look = 'None'

# ---------- sky + haze (world) ----------
world = bpy.data.worlds.new('TitanSky'); scene.world = world; world.use_nodes = True
nt = world.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputWorld')
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.9
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.50, 0.27, 0.09, 1)  # horizon = fog colour
ramp.color_ramp.elements[1].position = 0.7; ramp.color_ramp.elements[1].color = (0.10, 0.045, 0.02, 1) # zenith
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs[0], out.inputs['Surface'])

# Haze = distance fog on camera rays only (fast, noise-free, keeps GI untouched).
FOG_COLOR = (0.50, 0.27, 0.09, 1); FOG_DENSITY = 0.0055
def add_fog(mat):
    if not CFG['haze']: return
    t = mat.node_tree; o = t.nodes['Material Output']
    src = o.inputs['Surface'].links[0].from_socket
    lp = t.nodes.new('ShaderNodeLightPath')
    m1 = t.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = -FOG_DENSITY
    m2 = t.nodes.new('ShaderNodeMath'); m2.operation = 'EXPONENT'
    m3 = t.nodes.new('ShaderNodeMath'); m3.operation = 'SUBTRACT'; m3.inputs[0].default_value = 1.0
    m4 = t.nodes.new('ShaderNodeMath'); m4.operation = 'MULTIPLY'
    em = t.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = FOG_COLOR; em.inputs['Strength'].default_value = 0.9
    mix = t.nodes.new('ShaderNodeMixShader')
    t.links.new(lp.outputs['Ray Length'], m1.inputs[0]); t.links.new(m1.outputs[0], m2.inputs[0])
    t.links.new(m2.outputs[0], m3.inputs[1]); t.links.new(m3.outputs[0], m4.inputs[0])
    t.links.new(lp.outputs['Is Camera Ray'], m4.inputs[1]); t.links.new(m4.outputs[0], mix.inputs['Fac'])
    t.links.new(src, mix.inputs[1]); t.links.new(em.outputs[0], mix.inputs[2]); t.links.new(mix.outputs[0], o.inputs['Surface'])

# ---------- light ----------
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object
sun.data.energy = 2.6; sun.data.color = (1.0, 0.78, 0.55); sun.data.angle = math.radians(25)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))

# ---------- terrain ----------
if CFG['terrain']:
    n = Q['grid']; mesh = bpy.data.meshes.new('Terrain'); obj = bpy.data.objects.new('Terrain', mesh)
    scene.collection.objects.link(obj)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=SIZE / 2)
    layer = bm.verts.layers.float_color.new('Col')
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        p = Vector((x * 0.0045 + random_offset, y * 0.0045, 0))
        hills = noise.hybrid_multi_fractal(p, 1.0, 2.0, 5, 0.3, 1.0) * 18.0
        ch = noise.noise(Vector((x * 0.010 + random_offset, y * 0.010, 7.3)))
        valley = math.exp(-(ch / 0.07) ** 2)             # winding drainage-like channels
        v.co.z = hills - valley * 7.0
        v[layer] = (valley, 0, 0, 1)
    bm.to_mesh(mesh); bm.free()
    for p in mesh.polygons: p.use_smooth = True
    m = bpy.data.materials.new('TitanGround'); m.use_nodes = True; t = m.node_tree
    ca = t.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col'
    sp = t.nodes.new('ShaderNodeSeparateColor'); mx = t.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    mx.inputs['A'].default_value = (0.50, 0.27, 0.09, 1); mx.inputs['B'].default_value = (0.05, 0.025, 0.015, 1)
    nz = t.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.2; nz.inputs['Detail'].default_value = 6
    tco = t.nodes.new('ShaderNodeTexCoord'); big = t.nodes.new('ShaderNodeTexNoise')
    big.inputs['Scale'].default_value = 0.03; big.inputs['Detail'].default_value = 3
    tone = t.nodes.new('ShaderNodeMix'); tone.data_type = 'RGBA'
    tone.inputs['A'].default_value = (0.42, 0.21, 0.07, 1); tone.inputs['B'].default_value = (0.62, 0.36, 0.14, 1)
    t.links.new(tco.outputs['Object'], big.inputs['Vector']); t.links.new(big.outputs['Fac'], tone.inputs['Factor'])
    t.links.new(tone.outputs['Result'], mx.inputs['A'])
    bump = t.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.6
    bs = t.nodes['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.92
    t.links.new(ca.outputs['Color'], sp.inputs[0]); t.links.new(sp.outputs['Red'], mx.inputs['Factor'])
    t.links.new(mx.outputs['Result'], bs.inputs['Base Color'])
    t.links.new(nz.outputs['Fac'], bump.inputs['Height']); t.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    obj.data.materials.append(m)

# ---------- probe + parachute (simplified shapes, not a faithful model) ----------
Z0, Z1 = 46.0, 30.0   # probe altitude at start / end of shot
bpy.ops.object.empty_add(type='PLAIN_AXES'); rig = bpy.context.object; rig.name = 'ProbeRig'
for f, z in ((1, Z0), (TOTAL, Z1)):
    rig.location = (0, 0, z); rig.keyframe_insert('location', frame=f)
for f, r in ((1, -8), (TOTAL, 8)):   # slow swing under the chute
    rig.rotation_euler = (math.radians(r * 0.4), math.radians(r), 0); rig.keyframe_insert('rotation_euler', frame=f)
if CFG['probe']:
    mm = bpy.data.materials.new('Hull'); mm.use_nodes = True
    b = mm.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.55, 0.52, 0.48, 1)
    b.inputs['Metallic'].default_value = 0.6; b.inputs['Roughness'].default_value = 0.45
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0); body = bpy.context.object
    body.scale = (1, 1, 0.62); body.parent = rig; bpy.ops.object.shade_smooth(); body.data.materials.append(mm)

if CFG['parachute']:
    cm = bpy.data.materials.new('Canopy'); cm.use_nodes = True
    cb = cm.node_tree.nodes['Principled BSDF']; cb.inputs['Base Color'].default_value = (0.9, 0.85, 0.75, 1); cb.inputs['Roughness'].default_value = 0.8
    R, L = 2.8, 6.5
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=R, location=(0, 0, L)); can = bpy.context.object
    bm = bmesh.new(); bm.from_mesh(can.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.15 * R], context='VERTS'); bm.to_mesh(can.data); bm.free()
    can.parent = rig; bpy.ops.object.shade_smooth(); can.data.materials.append(cm)
    can.data.materials[0].use_backface_culling = False
    for i in range(12):                      # suspension lines
        a = i / 12 * 2 * math.pi; rim = Vector((math.cos(a) * R * 0.99, math.sin(a) * R * 0.99, L - 0.15 * R))
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=1)
        c = bpy.context.object; c.parent = rig; c.data.materials.append(cm)
        mid = (rim + Vector((0, 0, 0.2))) / 2; c.location = mid
        d = rim - Vector((0, 0, 0.2)); c.scale.z = d.length
        c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()

# ---------- camera: slow descending orbit that reveals terrain beneath the probe ----------
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0)); tgt = bpy.context.object; tgt.name = 'LookAt'
for f, z in ((1, Z0 + 2.0), (TOTAL, Z1 + 1.0)):
    tgt.location = (0, 0, z); tgt.keyframe_insert('location', frame=f)
bpy.ops.object.camera_add(); cam = bpy.context.object; scene.camera = cam
cam.data.lens = 24; cam.data.sensor_width = 36
for f, (ang, dist, dz) in ((1, (-40, 26, 6.0)), (TOTAL, (-8, 16, 3.0))):
    a = math.radians(ang)
    z = (Z0 if f == 1 else Z1) + dz
    cam.location = (math.sin(a) * dist, -math.cos(a) * dist, z); cam.keyframe_insert('location', frame=f)
tr = cam.constraints.new('TRACK_TO'); tr.target = tgt; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
if CFG['dof']:
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = rig; cam.data.dof.aperture_fstop = 4.5

for _m in bpy.data.materials:
    if _m.use_nodes: add_fog(_m)

bpy.ops.render.render(animation=True)
