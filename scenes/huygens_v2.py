# Huygens descent, version 2 (Titan). Headless:
#   blender -b -P scenes/huygens_v2.py -- --start 1 --end 72 --out /tmp/frames --quality draft
# Facts used (ESA): stabiliser chute ~3 m, disk-gap-band type; 36 angled spin vanes on the shell;
# pebble-like ice blocks seen at the surface; drainage channels. Shapes are artist concept, not CAD.
import bpy, bmesh, sys, math, random
from mathutils import Vector, Euler, Matrix, noise

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default
START = int(arg('--start', 1)); END = int(arg('--end', 72))
OUT = arg('--out', '/tmp/frames'); QUALITY = arg('--quality', 'draft'); SAMPLES = arg('--samples', None)

# what this shot uses (switch modules per subject)
CFG = dict(terrain=True, cobbles=True, haze=True, probe=True, parachute=True, dof=True)
Q = {'draft': dict(res=(960, 540), samples=40, seg=200, cobbles=4500),
     'final': dict(res=(1920, 1080), samples=96, seg=320, cobbles=6000)}[QUALITY]
TOTAL = 72
RMAX = 360.0
OFF = 11.7                      # change per episode for a different landscape
LAND = (6.0, 10.0)              # landing site (x, y)
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
scene.cycles.samples = int(SAMPLES) if SAMPLES else Q['samples']
scene.cycles.use_denoising = False          # apt Blender has no OIDN; temporal denoise happens in ffmpeg
scene.cycles.sample_clamp_indirect = 3.0; scene.cycles.sample_clamp_direct = 20.0
scene.cycles.max_bounces = 3
scene.render.resolution_x, scene.render.resolution_y = Q['res']
scene.render.fps = 12
scene.frame_start, scene.frame_end = START, END
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT + '/f_'
scene.view_settings.view_transform = 'Filmic'

# ---------- sky ----------
world = bpy.data.worlds.new('TitanSky'); scene.world = world; world.use_nodes = True
nt = world.node_tree; nt.nodes.clear()
wo = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.9
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.50, 0.27, 0.09, 1)
ramp.color_ramp.elements[1].position = 0.7; ramp.color_ramp.elements[1].color = (0.10, 0.045, 0.02, 1)
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs[0], wo.inputs['Surface'])

# haze = distance fog on camera rays (fast, noise-free)
FOG_COLOR = (0.50, 0.27, 0.09, 1); FOG_DENSITY = 0.0055
def add_fog(mat):
    if not CFG['haze']: return
    t = mat.node_tree; o = t.nodes['Material Output']; src = o.inputs['Surface'].links[0].from_socket
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
sun.data.energy = 2.8; sun.data.color = (1.0, 0.78, 0.55); sun.data.angle = math.radians(22)
sun.rotation_euler = (math.radians(58), 0, math.radians(35))

# ---------- terrain height field (shared by mesh and cobbles) ----------
def terrain_h(x, y):
    hills = noise.hybrid_multi_fractal(Vector((x * 0.0045 + OFF, y * 0.0045, 0)), 1.0, 2.0, 5, 0.3, 1.0) * 14.0
    mid = noise.fractal(Vector((x * 0.03 + OFF, y * 0.03, 2.1)), 1.0, 2.0, 4) * 1.6
    ch1 = noise.noise(Vector((x * 0.010 + OFF, y * 0.010, 7.3)))
    v1 = math.exp(-(ch1 / 0.07) ** 2)                               # main channels
    ch2 = noise.noise(Vector((x * 0.028 + OFF, y * 0.028, 3.7)))
    near = math.exp(-(ch1 / 0.30) ** 2)                             # tributaries only near main channels
    v2 = math.exp(-(ch2 / 0.06) ** 2) * near
    z = hills + mid - v1 * 6.0 - v2 * 2.0
    return z, max(v1, v2 * 0.85)

def build_terrain():
    S = Q['seg']; rings = []; r = 0.12
    while r < RMAX: rings.append(r); r *= 1.065        # dense rings near the origin, sparse far away
    bm = bmesh.new(); lay = bm.verts.layers.float_color.new('Col'); grid = []
    # centre the dense area on the landing site
    for r in rings:
        row = []
        for k in range(S):
            th = 2 * math.pi * k / S; x = LAND[0] + r * math.cos(th); y = LAND[1] + r * math.sin(th)
            z, val = terrain_h(x, y); v = bm.verts.new((x, y, z)); v[lay] = (val, 0, 0, 1); row.append(v)
        grid.append(row)
    for i in range(len(grid) - 1):
        for k in range(S):
            bm.faces.new((grid[i][k], grid[i + 1][k], grid[i + 1][(k + 1) % S], grid[i][(k + 1) % S]))
    bm.faces.new(grid[0])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('Terrain'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new('Terrain', me); scene.collection.objects.link(ob)
    m = bpy.data.materials.new('TitanGround'); m.use_nodes = True; t = m.node_tree
    ca = t.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col'
    sp = t.nodes.new('ShaderNodeSeparateColor'); mx = t.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    mx.inputs['B'].default_value = (0.045, 0.022, 0.012, 1)
    tco = t.nodes.new('ShaderNodeTexCoord'); big = t.nodes.new('ShaderNodeTexNoise')
    big.inputs['Scale'].default_value = 0.03; big.inputs['Detail'].default_value = 3
    tone = t.nodes.new('ShaderNodeMix'); tone.data_type = 'RGBA'
    tone.inputs['A'].default_value = (0.40, 0.20, 0.07, 1); tone.inputs['B'].default_value = (0.62, 0.36, 0.14, 1)
    vor = t.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 4.0
    fine = t.nodes.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value = 14.0; fine.inputs['Detail'].default_value = 8
    bump = t.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.9; bump.inputs['Distance'].default_value = 0.1
    bs = t.nodes['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.93
    t.links.new(tco.outputs['Object'], big.inputs['Vector']); t.links.new(big.outputs['Fac'], tone.inputs['Factor'])
    t.links.new(tone.outputs['Result'], mx.inputs['A']); t.links.new(ca.outputs['Color'], sp.inputs[0])
    t.links.new(sp.outputs['Red'], mx.inputs['Factor']); t.links.new(mx.outputs['Result'], bs.inputs['Base Color'])
    t.links.new(tco.outputs['Object'], vor.inputs['Vector']); t.links.new(tco.outputs['Object'], fine.inputs['Vector'])
    mixh = t.nodes.new('ShaderNodeMath'); mixh.operation = 'ADD'
    t.links.new(vor.outputs['Distance'], mixh.inputs[0]); t.links.new(fine.outputs['Fac'], mixh.inputs[1])
    t.links.new(mixh.outputs[0], bump.inputs['Height']); t.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    ob.data.materials.append(m)

def build_cobbles():
    bm = bmesh.new(); lay = bm.verts.layers.float_color.new('Col2'); kept = 0
    for _ in range(Q['cobbles']):
        r = 48.0 * random.random() ** 1.6; th = random.random() * 6.2832
        x = LAND[0] + r * math.cos(th); y = LAND[1] + r * math.sin(th); z, val = terrain_h(x, y)
        if random.random() > 0.55 + 0.45 * val: continue          # more stones in channel beds
        s = min(random.lognormvariate(math.log(0.13), 0.55), 0.8)
        sc = Matrix.Diagonal((s, s * random.uniform(0.7, 1.0), s * random.uniform(0.45, 0.7), 1.0))
        mat = Matrix.Translation((x, y, z + s * 0.08)) @ Euler((0, 0, random.random() * 6.28)).to_matrix().to_4x4() @ sc
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.5, matrix=mat); c = random.uniform(0.0, 1.0)
        for v in res['verts']: v[lay] = (c, 0, 0, 1)
        kept += 1
    me = bpy.data.meshes.new('Cobbles'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new('Cobbles', me); scene.collection.objects.link(ob)
    m = bpy.data.materials.new('IceCobble'); m.use_nodes = True; t = m.node_tree
    ca = t.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col2'; sp = t.nodes.new('ShaderNodeSeparateColor')
    mx = t.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    mx.inputs['A'].default_value = (0.15, 0.09, 0.06, 1); mx.inputs['B'].default_value = (0.40, 0.27, 0.17, 1)
    nz = t.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 25.0
    bump = t.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.4
    bs = t.nodes['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.78
    t.links.new(ca.outputs['Color'], sp.inputs[0]); t.links.new(sp.outputs['Red'], mx.inputs['Factor'])
    t.links.new(mx.outputs['Result'], bs.inputs['Base Color']); t.links.new(nz.outputs['Fac'], bump.inputs['Height'])
    t.links.new(bump.outputs['Normal'], bs.inputs['Normal']); ob.data.materials.append(m)
    return kept

# ---------- probe, parachute (disk-gap-band), lines ----------
def revolve(profile, seg=96, ripple=0.0, lobes=12):
    bm = bmesh.new(); rows = []
    for (r, z) in profile:
        rows.append([bm.verts.new((r * (1 + ripple * math.sin(lobes * 2 * math.pi * k / seg)) * math.cos(2 * math.pi * k / seg),
                                   r * (1 + ripple * math.sin(lobes * 2 * math.pi * k / seg)) * math.sin(2 * math.pi * k / seg), z))
                     for k in range(seg)])
    for i in range(len(rows) - 1):
        for k in range(seg): bm.faces.new((rows[i][k], rows[i][(k + 1) % seg], rows[i + 1][(k + 1) % seg], rows[i + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm

def to_obj(bm, name, mat, parent):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob); ob.parent = parent; ob.data.materials.append(mat); return ob

rig = bpy.data.objects.new('ProbeRig', None); scene.collection.objects.link(rig)
CHUTE_R, LINE_L = 1.515, 3.6        # 3.03 m stabiliser chute
if CFG['probe']:
    al = bpy.data.materials.new('Aluminium'); al.use_nodes = True; b = al.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.62, 0.60, 0.57, 1); b.inputs['Metallic'].default_value = 0.85; b.inputs['Roughness'].default_value = 0.38
    foil = bpy.data.materials.new('Foil'); foil.use_nodes = True; f = foil.node_tree.nodes['Principled BSDF']
    f.inputs['Base Color'].default_value = (0.75, 0.55, 0.20, 1); f.inputs['Metallic'].default_value = 0.9; f.inputs['Roughness'].default_value = 0.25
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.65, matrix=Matrix.Diagonal((1, 1, 0.45, 1)))
    for i in range(36):                                   # 36 angled spin vanes
        th = 2 * math.pi * i / 36
        m = Matrix.Rotation(th, 4, 'Z') @ Matrix.Translation((0.66, 0, 0)) @ Matrix.Rotation(math.radians(35), 4, 'X') @ Matrix.Diagonal((0.012, 0.19, 0.10, 1))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    to_obj(bm, 'DescentModule', al, rig)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=0.2, radius2=0.2, depth=0.14, matrix=Matrix.Translation((0, 0, 0.36)))
    to_obj(bm, 'ChuteCanister', foil, rig)
if CFG['parachute']:
    cm = bpy.data.materials.new('Canopy'); cm.use_nodes = True; cb = cm.node_tree.nodes['Principled BSDF']
    cb.inputs['Base Color'].default_value = (0.92, 0.88, 0.80, 1); cb.inputs['Roughness'].default_value = 0.85
    try: cb.inputs['Transmission Weight'].default_value = 0.25
    except Exception: pass
    R = CHUTE_R
    disk = [(0.01 + 0.59 * R * i / 10, LINE_L + R * (0.02 + 0.16 * (1 - (0.59 * i / 10 / 0.6) ** 2))) for i in range(11)]
    band = [(0.68 * R + 0.32 * R * t + 0.05 * R * math.sin(math.pi * t), LINE_L - 0.32 * R * t) for t in [i / 10 for i in range(11)]]
    for name, prof, rp in (('ChuteDisk', disk, 0.012), ('ChuteBand', band, 0.03)):
        ob = to_obj(revolve(prof, 96, rp, 12), name, cm, rig)
        sol = ob.modifiers.new('Cloth', 'SOLIDIFY'); sol.thickness = 0.01
    bm = bmesh.new(); top = Vector((0, 0, 0.42))
    for i in range(16):
        a = 2 * math.pi * i / 16; rim = Vector((math.cos(a) * R, math.sin(a) * R, LINE_L - 0.32 * R)); d = rim - top
        bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=0.006, radius2=0.006, depth=d.length,
                              matrix=Matrix.Translation((top + rim) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4())
    lm = bpy.data.materials.new('Lines'); lm.use_nodes = True; lm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.9, 0.85, 0.7, 1)
    to_obj(bm, 'SuspensionLines', lm, rig)

if CFG['terrain']: build_terrain()
KEPT = build_cobbles() if CFG['cobbles'] else 0
H_LAND = terrain_h(*LAND)[0]

# ---------- motion: constant descent with drift, spin and sway; camera arcs from wide-high to low ----------
def ease(t): return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
tgt = bpy.data.objects.new('LookAt', None); scene.collection.objects.link(tgt)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.data.lens = 24; cam.data.sensor_width = 36
tr = cam.constraints.new('TRACK_TO'); tr.target = tgt; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
if CFG['dof']:
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = rig; cam.data.dof.aperture_fstop = 4.5
frames = list(range(1, TOTAL + 1, 6)) + [TOTAL]
for f in frames:
    t = (f - 1) / (TOTAL - 1); e = ease(t)
    rx, ry = lerp(-9, LAND[0], t), lerp(-12, LAND[1], t); rz = H_LAND + lerp(34.0, 1.0, t)        # constant descent
    rig.location = (rx, ry, rz); rig.rotation_euler = (math.radians(3 * math.sin(6.28 * t * 1.3)), math.radians(3 * math.sin(6.28 * t * 0.9 + 1)), math.radians(-55 * t))
    rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f)
    ang = math.radians(lerp(-55, 15, e)); dist = lerp(20, 8.5, e)
    cam.location = (rx + math.sin(ang) * dist, ry - math.cos(ang) * dist, rz + lerp(7.0, 0.5, e)); cam.keyframe_insert('location', frame=f)
    tgt.location = (rx, ry, rz + lerp(2.0, 1.4, e)); tgt.keyframe_insert('location', frame=f)

for _m in bpy.data.materials:
    if _m.use_nodes: add_fog(_m)
print('COBBLES', KEPT, 'H_LAND', round(H_LAND, 2))
bpy.ops.render.render(animation=True)
