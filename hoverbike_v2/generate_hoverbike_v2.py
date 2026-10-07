import sys
import os
import math
import subprocess
import bpy

# Add current and project root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import blender_utils

def ensure_textures():
    tex_dir = os.path.abspath("hoverbike_v2/textures")
    terracotta_path = os.path.join(tex_dir, "terracotta_hull.png")
    if not os.path.exists(terracotta_path):
        gen_script = os.path.abspath("hoverbike_v2/generate_textures.py")
        print("Executing texture generator in system python...")
        subprocess.run(["python3", gen_script], check=True)

def create_hoverbike_v2():
    ensure_textures()
    tex_dir = os.path.abspath("hoverbike_v2/textures")

    # Reset scene
    blender_utils.reset_scene()

    # Materials with Image Texture Maps
    mat_hull_primary = blender_utils.create_image_texture_material(
        "HullPrimary_Terracotta",
        image_path=os.path.join(tex_dir, "terracotta_hull.png"),
        metallic=0.15,
        roughness=0.5
    )

    mat_hull_secondary = blender_utils.create_image_texture_material(
        "HullSecondary_Cream",
        image_path=os.path.join(tex_dir, "cream_panel.png"),
        metallic=0.05,
        roughness=0.6
    )

    mat_dark_chassis = blender_utils.create_image_texture_material(
        "DarkChassis_Steel",
        image_path=os.path.join(tex_dir, "chassis_dark.png"),
        metallic=0.6,
        roughness=0.4
    )

    mat_accent_brass = blender_utils.create_stylized_material(
        "Accent_Brass",
        color=(0.85, 0.62, 0.25, 1.0), # Antique brass/gold accent
        metallic=0.8,
        roughness=0.3
    )

    mat_glow_cyan = blender_utils.create_stylized_material(
        "Glow_Cyan",
        color=(0.0, 0.95, 0.95, 1.0),
        emission_color=(0.0, 1.0, 1.0, 1.0),
        emission_strength=8.0
    )

    mat_canopy_glass = blender_utils.create_stylized_material(
        "Canopy_Glass",
        color=(0.25, 0.85, 0.80, 0.5), # Translucent teal tint
        metallic=0.1,
        roughness=0.1
    )

    mat_pilot_suit = blender_utils.create_image_texture_material(
        "Pilot_Suit",
        image_path=os.path.join(tex_dir, "pilot_suit.png"),
        metallic=0.1,
        roughness=0.7
    )

    # Main collection
    hoverbike_coll = bpy.data.collections.new("HoverbikeV2")
    bpy.context.scene.collection.children.link(hoverbike_coll)

    # Helper function to assign collection, UV unwrap, & material
    def setup_obj(obj, name, material, parent=None, smooth=True, unwrap=True):
        obj.name = name
        hoverbike_coll.objects.link(obj)
        if unwrap and obj.type == 'MESH':
            blender_utils.smart_uv_unwrap(obj)
        if material:
            obj.data.materials.append(material)
        if parent:
            obj.parent = parent
        if smooth and hasattr(obj.data, "polygons"):
            for poly in obj.data.polygons:
                poly.use_smooth = True
        return obj

    # 1. Main Compact & Rounded Fuselage
    # Base chassis core
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    chassis = bpy.context.active_object
    chassis.scale = (0.75, 1.5, 0.5)
    setup_obj(chassis, "Chassis_Core", mat_dark_chassis, smooth=False)

    # Upper primary rounded hull shell (terracotta)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=1.4, vertices=24, location=(0, 0.0, 0.75))
    hull_upper = bpy.context.active_object
    hull_upper.rotation_euler = (math.radians(90), 0, 0)
    hull_upper.scale = (1.0, 0.75, 1.0)
    setup_obj(hull_upper, "Hull_Upper", mat_hull_primary, parent=chassis)

    # Rounded Nose Cone (Sphere/Dome style matching concept art)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.46, location=(0, 0.8, 0.75))
    nose = bpy.context.active_object
    nose.scale = (1.0, 1.2, 0.72)
    setup_obj(nose, "Hull_Nose", mat_hull_primary, parent=chassis)

    # Front Air Intake Scoop (integrated into nose)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.2, vertices=16, location=(0, 1.32, 0.72))
    intake = bpy.context.active_object
    intake.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(intake, "Intake_Scoop", mat_dark_chassis, parent=nose)

    # Front Intake Inner Glow Core
    bpy.ops.mesh.primitive_circle_add(radius=0.18, fill_type='NGON', location=(0, 1.42, 0.72))
    intake_glow = bpy.context.active_object
    intake_glow.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(intake_glow, "Intake_GlowCore", mat_glow_cyan, parent=intake, unwrap=False)

    # Rounded Side Shell Panels (Cream Stone contrast panels flush on flanks)
    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.1, vertices=16, location=(sign * 0.42, 0.0, 0.65))
        panel = bpy.context.active_object
        panel.rotation_euler = (math.radians(90), 0, 0)
        panel.scale = (0.25, 0.6, 1.0)
        setup_obj(panel, f"SidePanel_{side}", mat_hull_secondary, parent=chassis)

    # 2. Cockpit Interior & Pilot Driver
    # Cockpit Cavity / Seat
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.25, 0.75))
    seat_back = bpy.context.active_object
    seat_back.scale = (0.42, 0.12, 0.45)
    seat_back.rotation_euler = (math.radians(-25), 0, 0)
    setup_obj(seat_back, "Seat_Backrest", mat_dark_chassis, parent=chassis, smooth=False)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.1, 0.62))
    seat_cushion = bpy.context.active_object
    seat_cushion.scale = (0.44, 0.4, 0.1)
    setup_obj(seat_cushion, "Seat_Cushion", mat_dark_chassis, parent=chassis, smooth=False)

    # Steering Console / Handlebars
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.6, vertices=12, location=(0, 0.25, 0.85))
    handlebar = bpy.context.active_object
    handlebar.rotation_euler = (0, math.radians(90), 0)
    setup_obj(handlebar, "Handlebar", mat_accent_brass, parent=chassis)

    # Dashboard Console
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.38, 0.82))
    dash = bpy.context.active_object
    dash.scale = (0.35, 0.15, 0.18)
    dash.rotation_euler = (math.radians(-30), 0, 0)
    setup_obj(dash, "Dash_Console", mat_dark_chassis, parent=chassis, smooth=False)

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0.35, 0.88))
    screen = bpy.context.active_object
    screen.scale = (0.28, 0.12, 1.0)
    screen.rotation_euler = (math.radians(-30), 0, 0)
    setup_obj(screen, "Dash_Screen_Glow", mat_glow_cyan, parent=dash, unwrap=False)

    # PILOT DRIVER MODEL (Seated inside cockpit)
    pilot_root = bpy.data.objects.new("Pilot_Driver", None)
    hoverbike_coll.objects.link(pilot_root)
    pilot_root.parent = chassis

    # Pilot Torso / Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.2, 0.82))
    torso = bpy.context.active_object
    torso.scale = (0.32, 0.24, 0.38)
    torso.rotation_euler = (math.radians(-15), 0, 0)
    setup_obj(torso, "Pilot_Torso", mat_pilot_suit, parent=pilot_root, smooth=False)

    # Pilot Head / Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.16, location=(0, -0.22, 1.12))
    head = bpy.context.active_object
    setup_obj(head, "Pilot_Helmet", mat_pilot_suit, parent=pilot_root)

    # Pilot Visor (Glowing Cyan)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.08, vertices=12, location=(0, -0.12, 1.13))
    visor = bpy.context.active_object
    visor.rotation_euler = (math.radians(80), 0, 0)
    visor.scale = (0.9, 0.4, 0.9)
    setup_obj(visor, "Pilot_Visor", mat_glow_cyan, parent=head, unwrap=False)

    # Pilot Arms holding handlebar
    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.35, vertices=8, location=(sign * 0.22, 0.02, 0.88))
        arm = bpy.context.active_object
        arm.rotation_euler = (math.radians(65), math.radians(sign * -25), 0)
        setup_obj(arm, f"Pilot_Arm_{side}", mat_pilot_suit, parent=pilot_root)

    # 3. ANIMATED CANOPY ASSEMBLY (Pivoted for forward opening)
    canopy_assembly = bpy.data.objects.new("Canopy_Assembly", None)
    hoverbike_coll.objects.link(canopy_assembly)
    canopy_assembly.parent = chassis
    canopy_assembly.location = (0, 0.05, 0.82)

    # Sleek Windshield / Glass Canopy Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.52, location=(0, -0.05, 0.12))
    canopy = bpy.context.active_object
    canopy.scale = (0.82, 1.25, 0.68)
    canopy.rotation_euler = (math.radians(10), 0, 0)
    setup_obj(canopy, "Canopy_GlassDome", mat_canopy_glass, parent=canopy_assembly, unwrap=False)

    # Canopy Brass Frame Trim
    bpy.ops.mesh.primitive_torus_add(major_radius=0.46, minor_radius=0.02, major_segments=24, minor_segments=8, location=(0, -0.05, 0.12))
    canopy_frame = bpy.context.active_object
    canopy_frame.scale = (0.83, 1.24, 0.66)
    canopy_frame.rotation_euler = (math.radians(10), 0, 0)
    setup_obj(canopy_frame, "Canopy_Frame", mat_accent_brass, parent=canopy_assembly)

    # 4. Rear Engine Reactor & Thruster Exhaust
    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.6, vertices=20, location=(0, -0.85, 0.65))
    engine_housing = bpy.context.active_object
    engine_housing.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(engine_housing, "Engine_Housing", mat_dark_chassis, parent=chassis)

    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.36, radius2=0.25, depth=0.35, location=(0, -1.2, 0.65))
    thruster_nozzle = bpy.context.active_object
    thruster_nozzle.rotation_euler = (math.radians(-90), 0, 0)
    setup_obj(thruster_nozzle, "Thruster_Nozzle", mat_hull_secondary, parent=engine_housing)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.1, vertices=16, location=(0, -1.35, 0.65))
    thruster_glow = bpy.context.active_object
    thruster_glow.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(thruster_glow, "Thruster_GlowCore", mat_glow_cyan, parent=thruster_nozzle, unwrap=False)

    # 5. Anti-Gravity Thruster Pods (4 Integrated & Connected Outriggers)
    pod_positions = [
        ("Front_Left", -0.68, 0.50, 0.42, -20),
        ("Front_Right", 0.68, 0.50, 0.42, 20),
        ("Rear_Left", -0.72, -0.50, 0.42, -18),
        ("Rear_Right", 0.72, -0.50, 0.42, 18),
    ]

    for name_suffix, x, y, z, roll in pod_positions:
        sign = -1 if x < 0 else 1

        strut_center_x = sign * (0.35 + abs(x)) / 2.0
        strut_length = abs(x) - 0.30

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(strut_center_x, y, z + 0.1))
        strut = bpy.context.active_object
        strut.scale = (strut_length, 0.22, 0.08)
        strut.rotation_euler = (0, math.radians(roll * 0.4), 0)
        setup_obj(strut, f"Strut_{name_suffix}", mat_dark_chassis, parent=chassis, smooth=False)

        # Thruster Pod Housing
        bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.5, vertices=16, location=(x, y, z))
        pod = bpy.context.active_object
        pod.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(pod, f"Pod_Housing_{name_suffix}", mat_hull_primary, parent=strut)

        # Top Brass Cap
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.25, radius2=0.15, depth=0.12, location=(x, y, z + 0.26))
        cap = bpy.context.active_object
        cap.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(cap, f"Pod_Cap_{name_suffix}", mat_accent_brass, parent=pod)

        # Underside Anti-Grav Emitter Glow Disc
        bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.06, vertices=16, location=(x, y, z - 0.24))
        emitter = bpy.context.active_object
        emitter.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(emitter, f"Pod_EmitterGlow_{name_suffix}", mat_glow_cyan, parent=pod, unwrap=False)

        # Outer Emitter Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.02, major_segments=16, minor_segments=8, location=(x, y, z - 0.24))
        ring = bpy.context.active_object
        ring.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(ring, f"Pod_EmitterRing_{name_suffix}", mat_hull_secondary, parent=pod)

    # 6. Tail Fins / Aerodynamic Stabilizers
    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.38, -0.9, 1.05))
        fin = bpy.context.active_object
        fin.scale = (0.04, 0.35, 0.3)
        fin.rotation_euler = (math.radians(-20), math.radians(sign * 18), 0)
        setup_obj(fin, f"TailFin_{side}", mat_hull_primary, parent=chassis, smooth=False)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.40, -0.95, 1.18))
        fin_trim = bpy.context.active_object
        fin_trim.scale = (0.02, 0.32, 0.04)
        fin_trim.rotation_euler = (math.radians(-20), math.radians(sign * 18), 0)
        setup_obj(fin_trim, f"TailFin_Trim_{side}", mat_accent_brass, parent=fin, smooth=False)

    return chassis

def main():
    print("Generating Textured Hoverbike V2 Model...")
    create_hoverbike_v2()

    # Save Blender file
    blend_path = os.path.abspath("hoverbike_v2/hoverbike_v2.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved .blend file to: {blend_path}")

    # Export GLB
    glb_path = os.path.abspath("hoverbike_v2/hoverbike_v2.glb")
    blender_utils.export_model(glb_path)
    print(f"Exported .glb file to: {glb_path}")

    # Set up lighting and background world
    blender_utils.add_three_point_lighting()

    world = bpy.data.worlds.new('HoverbikeWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.12, 0.10, 0.15, 1.0)
        bg_node.inputs['Strength'].default_value = 1.2

    # Render visual captures
    camera_views = [
        ("angle_front_quarter", (2.2, -2.8, 1.8), (0, 0, 0.6)),
        ("angle_rear_quarter", (-2.2, -2.4, 1.6), (0, -0.3, 0.6)),
        ("angle_side_profile", (3.2, 0.0, 0.8), (0, 0, 0.6)),
        ("angle_top_down", (0.1, -0.1, 4.2), (0, 0, 0.5)),
    ]

    for view_name, cam_pos, target_pos in camera_views:
        blender_utils.setup_camera(location=cam_pos, target_location=target_pos, lens=45)
        output_file = os.path.abspath(f"hoverbike_v2/captures/{view_name}.png")
        blender_utils.configure_render(output_file, resolution=(1024, 1024))
        bpy.ops.render.render(write_still=True)
        print(f"Rendered capture: {output_file}")

if __name__ == "__main__":
    main()
