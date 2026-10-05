import bpy
import math
import os

def reset_scene():
    """Clear all mesh, light, camera objects and collections."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

def setup_camera(location=(0, -5, 5), target_location=(0, 0, 0), lens=50):
    """Set up camera looking at target_location."""
    cam_data = bpy.data.cameras.new(name='MainCamera')
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new('MainCamera', cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

    cam_obj.location = location

    # Point camera at target
    direction = [t - c for t, c in zip(target_location, location)]
    rot_x = math.atan2(math.hypot(direction[0], direction[1]), direction[2])
    rot_z = math.atan2(direction[1], direction[0]) + math.pi / 2
    cam_obj.rotation_euler = (rot_x, 0, rot_z)

    bpy.context.scene.camera = cam_obj
    return cam_obj

def add_three_point_lighting(intensity=1000):
    """Add a key, fill, and rim light for stylized presentation."""
    # Key light
    key_data = bpy.data.lights.new(name='KeyLight', type='SUN')
    key_data.energy = 4.0
    key_data.color = (1.0, 0.95, 0.85) # warm sunlight
    key_obj = bpy.data.objects.new('KeyLight', key_data)
    key_obj.location = (5, -5, 8)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))
    bpy.context.scene.collection.objects.link(key_obj)

    # Fill light
    fill_data = bpy.data.lights.new(name='FillLight', type='SUN')
    fill_data.energy = 1.8
    fill_data.color = (0.4, 0.6, 0.8) # cool ambient fill
    fill_obj = bpy.data.objects.new('FillLight', fill_data)
    fill_obj.location = (-5, -5, 4)
    fill_obj.rotation_euler = (math.radians(60), math.radians(-20), math.radians(-45))
    bpy.context.scene.collection.objects.link(fill_obj)

    # Rim light
    rim_data = bpy.data.lights.new(name='RimLight', type='POINT')
    rim_data.energy = 150.0
    rim_data.color = (0.9, 0.7, 0.4) # golden rim accent
    rim_obj = bpy.data.objects.new('RimLight', rim_data)
    rim_obj.location = (0, 4, 3)
    bpy.context.scene.collection.objects.link(rim_obj)

def create_stylized_material(name, color=(0.8, 0.7, 0.5, 1.0), metallic=0.1, roughness=0.6, emission_color=None, emission_strength=0.0):
    """Create a Principled BSDF material with lowpoly/stylized properties."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    bsdf = nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emission_color and 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

def configure_render(filepath, resolution=(1080, 1080), engine='CYCLES'):
    """Configure render settings for headless rendering using Cycles CPU fallback."""
    scene = bpy.context.scene

    # CYCLES on CPU is guaranteed to work headlessly without X11 or GPU context
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = False

    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    scene.render.filepath = filepath

def export_model(filepath):
    """Export scene or active object as .gltf/.glb or .obj."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.export_scene.gltf(filepath=filepath)
    elif filepath.endswith('.obj'):
        bpy.ops.wm.obj_export(filepath=filepath)
