import sys
import os
import math
import bpy

# Add project root directory to path to import blender_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import blender_utils

def create_hoverbike_v2():
    # Reset scene
    blender_utils.reset_scene()

    # Materials
    mat_hull_primary = blender_utils.create_stylized_material(
        "HullPrimary_Terracotta",
        color=(0.85, 0.38, 0.22, 1.0), # SABLE style terracotta orange
        metallic=0.15,
        roughness=0.5
    )

    mat_hull_secondary = blender_utils.create_stylized_material(
        "HullSecondary_Cream",
        color=(0.92, 0.88, 0.80, 1.0), # Desert stone cream
        metallic=0.05,
        roughness=0.6
    )

    mat_dark_chassis = blender_utils.create_stylized_material(
        "DarkChassis_Steel",
        color=(0.18, 0.20, 0.23, 1.0), # Dark slate gray steel
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
        color=(0.25, 0.85, 0.80, 0.6), # Translucent teal tint
        metallic=0.1,
        roughness=0.1
    )

    # Main collection
    hoverbike_coll = bpy.data.collections.new("HoverbikeV2")
    bpy.context.scene.collection.children.link(hoverbike_coll)

    # Helper function to assign collection & material
    def setup_obj(obj, name, material, parent=None):
        obj.name = name
        hoverbike_coll.objects.link(obj)
        if material:
            obj.data.materials.append(material)
        if parent:
            obj.parent = parent
        return obj

    # 1. Main Fuselage / Body Hull
    bpy.ops.mesh.add_subdivided_cube = False # Use standard cylinder / mesh creation

    # Base chassis core (long, streamlined tapered box)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.6))
    chassis = bpy.context.active_object
    chassis.scale = (0.7, 2.6, 0.5)
    setup_obj(chassis, "Chassis_Core", mat_dark_chassis)

    # Upper primary hull shell (terracotta)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=2.4, vertices=12, location=(0, 0.1, 0.85))
    hull_upper = bpy.context.active_object
    hull_upper.rotation_euler = (math.radians(90), 0, 0)
    hull_upper.scale = (1.0, 0.7, 1.0)
    setup_obj(hull_upper, "Hull_Upper", mat_hull_primary, parent=chassis)

    # Nose Cone / Front Shield (tapered & angled)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.48, radius2=0.15, depth=1.2, location=(0, 1.7, 0.8))
    nose = bpy.context.active_object
    nose.rotation_euler = (math.radians(-90), 0, 0)
    setup_obj(nose, "Hull_Nose", mat_hull_primary, parent=chassis)

    # Front Air Intake Scoop (dark interior with brass grille frame)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.3, vertices=8, location=(0, 2.25, 0.75))
    intake = bpy.context.active_object
    intake.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(intake, "Intake_Scoop", mat_dark_chassis, parent=nose)

    # Front Intake Inner Glow Core
    bpy.ops.mesh.primitive_circle_add(radius=0.16, fill_type='NGON', location=(0, 2.38, 0.75))
    intake_glow = bpy.context.active_object
    intake_glow.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(intake_glow, "Intake_GlowCore", mat_glow_cyan, parent=intake)

    # Side Shell Panels (Cream Stone contrast panels on flanks)
    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.42, 0.2, 0.75))
        panel = bpy.context.active_object
        panel.scale = (0.08, 1.8, 0.35)
        panel.rotation_euler = (0, math.radians(sign * 15), 0)
        setup_obj(panel, f"SidePanel_{side}", mat_hull_secondary, parent=chassis)

    # 2. Cockpit Interior & Canopy Dome
    # Cockpit Cavity / Seat
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.2, 0.9))
    seat_back = bpy.context.active_object
    seat_back.scale = (0.4, 0.1, 0.5)
    seat_back.rotation_euler = (math.radians(-20), 0, 0)
    setup_obj(seat_back, "Seat_Backrest", mat_dark_chassis, parent=chassis)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05, 0.7))
    seat_cushion = bpy.context.active_object
    seat_cushion.scale = (0.42, 0.45, 0.1)
    setup_obj(seat_cushion, "Seat_Cushion", mat_dark_chassis, parent=chassis)

    # Steering Console / Handlebars
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.7, vertices=8, location=(0, 0.45, 0.95))
    handlebar = bpy.context.active_object
    handlebar.rotation_euler = (0, math.radians(90), 0)
    setup_obj(handlebar, "Handlebar", mat_accent_brass, parent=chassis)

    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.15, vertices=8, location=(sign * 0.35, 0.45, 0.95))
        grip = bpy.context.active_object
        grip.rotation_euler = (0, math.radians(90), 0)
        setup_obj(grip, f"Handlebar_Grip_{side}", mat_dark_chassis, parent=handlebar)

    # Cockpit Display / Dash
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.55, 0.92))
    dash = bpy.context.active_object
    dash.scale = (0.35, 0.15, 0.2)
    dash.rotation_euler = (math.radians(-30), 0, 0)
    setup_obj(dash, "Dash_Console", mat_dark_chassis, parent=chassis)

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0.52, 0.98))
    screen = bpy.context.active_object
    screen.scale = (0.28, 0.12, 1.0)
    screen.rotation_euler = (math.radians(-30), 0, 0)
    setup_obj(screen, "Dash_Screen_Glow", mat_glow_cyan, parent=dash)

    # Sleek Windshield / Glass Canopy Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.55, location=(0, 0.1, 0.95))
    canopy = bpy.context.active_object
    canopy.scale = (0.85, 1.9, 0.7)
    canopy.rotation_euler = (math.radians(10), 0, 0)
    setup_obj(canopy, "Canopy_GlassDome", mat_canopy_glass, parent=chassis)

    # Canopy Brass Frame Ridge
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.02, major_segments=16, minor_segments=6, location=(0, 0.1, 0.95))
    canopy_frame = bpy.context.active_object
    canopy_frame.scale = (0.86, 1.88, 0.68)
    canopy_frame.rotation_euler = (math.radians(10), 0, 0)
    setup_obj(canopy_frame, "Canopy_Frame", mat_accent_brass, parent=canopy)

    # 3. Rear Main Engine Reactor & Thruster Exhaust
    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.8, vertices=12, location=(0, -1.35, 0.75))
    engine_housing = bpy.context.active_object
    engine_housing.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(engine_housing, "Engine_Housing", mat_dark_chassis, parent=chassis)

    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.36, radius2=0.25, depth=0.4, location=(0, -1.8, 0.75))
    thruster_nozzle = bpy.context.active_object
    thruster_nozzle.rotation_euler = (math.radians(-90), 0, 0)
    setup_obj(thruster_nozzle, "Thruster_Nozzle", mat_hull_secondary, parent=engine_housing)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.1, vertices=12, location=(0, -1.98, 0.75))
    thruster_glow = bpy.context.active_object
    thruster_glow.rotation_euler = (math.radians(90), 0, 0)
    setup_obj(thruster_glow, "Thruster_GlowCore", mat_glow_cyan, parent=thruster_nozzle)

    # 4. Anti-Gravity Thruster Pods (4 Angled Outriggers: Front L/R, Rear L/R)
    pod_positions = [
        ("Front_Left", -0.9, 0.9, 0.45, -25),
        ("Front_Right", 0.9, 0.9, 0.45, 25),
        ("Rear_Left", -1.0, -0.9, 0.45, -20),
        ("Rear_Right", 1.0, -0.9, 0.45, 20),
    ]

    for name_suffix, x, y, z, roll in pod_positions:
        # Supporting Wing Strut (connecting chassis to pod)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x * 0.5, y, z + 0.15))
        strut = bpy.context.active_object
        strut.scale = (0.45, 0.15, 0.05)
        strut.rotation_euler = (0, math.radians(roll * 0.5), math.radians(-10 if y > 0 else 10))
        setup_obj(strut, f"Strut_{name_suffix}", mat_dark_chassis, parent=chassis)

        # Thruster Pod Housing
        bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.6, vertices=10, location=(x, y, z))
        pod = bpy.context.active_object
        pod.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(pod, f"Pod_Housing_{name_suffix}", mat_hull_primary, parent=strut)

        # Top Brass Cap
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.29, radius2=0.18, depth=0.15, location=(x, y, z + 0.32))
        cap = bpy.context.active_object
        cap.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(cap, f"Pod_Cap_{name_suffix}", mat_accent_brass, parent=pod)

        # Underside Anti-Grav Emitter Glow Disc
        bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.08, vertices=12, location=(x, y, z - 0.28))
        emitter = bpy.context.active_object
        emitter.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(emitter, f"Pod_EmitterGlow_{name_suffix}", mat_glow_cyan, parent=pod)

        # Outer Emitter Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.26, minor_radius=0.025, major_segments=12, minor_segments=6, location=(x, y, z - 0.28))
        ring = bpy.context.active_object
        ring.rotation_euler = (0, math.radians(roll * 0.3), 0)
        setup_obj(ring, f"Pod_EmitterRing_{name_suffix}", mat_hull_secondary, parent=pod)

    # 5. Rear Tail Fins / Aerodynamic Stabilizers
    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.45, -1.4, 1.2))
        fin = bpy.context.active_object
        fin.scale = (0.04, 0.4, 0.35)
        fin.rotation_euler = (math.radians(-25), math.radians(sign * 20), 0)
        setup_obj(fin, f"TailFin_{side}", mat_hull_primary, parent=chassis)

        # Brass Accent Edge on Fin
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.47, -1.45, 1.35))
        fin_trim = bpy.context.active_object
        fin_trim.scale = (0.02, 0.38, 0.05)
        fin_trim.rotation_euler = (math.radians(-25), math.radians(sign * 20), 0)
        setup_obj(fin_trim, f"TailFin_Trim_{side}", mat_accent_brass, parent=fin)

    # Return main chassis root
    return chassis

def main():
    print("Generating Hoverbike V2 Model...")
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
        bg_node.inputs['Color'].default_value = (0.12, 0.10, 0.15, 1.0) # Soft desert ambient twilight
        bg_node.inputs['Strength'].default_value = 1.2

    # Define camera views for captures
    camera_views = [
        ("angle_front_quarter", (2.8, -3.8, 2.2), (0, 0, 0.7)),
        ("angle_rear_quarter", (-2.8, -3.2, 2.0), (0, -0.5, 0.7)),
        ("angle_side_profile", (4.2, 0.0, 1.0), (0, 0, 0.7)),
        ("angle_top_down", (0.1, -0.1, 5.5), (0, 0, 0.6)),
    ]

    for view_name, cam_pos, target_pos in camera_views:
        blender_utils.setup_camera(location=cam_pos, target_location=target_pos, lens=45)
        output_file = os.path.abspath(f"hoverbike_v2/captures/{view_name}.png")
        blender_utils.configure_render(output_file, resolution=(1024, 1024))
        bpy.ops.render.render(write_still=True)
        print(f"Rendered capture: {output_file}")

if __name__ == "__main__":
    main()
