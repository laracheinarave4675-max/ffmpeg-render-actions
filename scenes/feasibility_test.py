# Feasibility test: a planet with a procedural surface and a slow camera push-in.
# Runs headless: blender -b -P scenes/feasibility_test.py
import bpy, math

# Clean the default scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Render settings: CPU Cycles, low samples (no GPU on GitHub runners)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = False
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 120  # 5 seconds
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '/tmp/blender_frames/f_'

# Black space background
world = bpy.data.worlds.new('Space')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.0, 0.0, 0.005, 1)

# Planet with procedural noise surface
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.0, location=(0, 0, 0))
planet = bpy.context.object
bpy.ops.object.shade_smooth()
mat = bpy.data.materials.new('Surface')
mat.use_nodes = True
nt = mat.node_tree
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 6.0
noise.inputs['Detail'].default_value = 8.0
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.45, 0.2, 0.05, 1)
ramp.color_ramp.elements[1].color = (0.9, 0.55, 0.2, 1)
bsdf = nt.nodes['Principled BSDF']
nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
planet.data.materials.append(mat)

# Slow planet rotation
planet.rotation_euler = (0, 0, 0)
planet.keyframe_insert('rotation_euler', frame=1)
planet.rotation_euler = (0, 0, math.radians(30))
planet.keyframe_insert('rotation_euler', frame=120)

# Sun light from the side
bpy.ops.object.light_add(type='SUN', location=(5, -5, 3))
sun = bpy.context.object
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(50), 0, math.radians(40))

# Camera pushing in toward the planet
bpy.ops.object.camera_add(location=(0, -6, 0.5))
cam = bpy.context.object
cam.rotation_euler = (math.radians(86), 0, 0)
scene.camera = cam
cam.keyframe_insert('location', frame=1)
cam.location = (0, -3.2, 0.3)
cam.keyframe_insert('location', frame=120)

bpy.ops.render.render(animation=True)
