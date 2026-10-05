import sys
import os
import math
import bmesh

# Add root directory to sys.path to import blender_utils
sys.path.append(os.path.abspath("."))
import blender_utils

import bpy

def mathutils_rotation_matrix_x(angle_deg):
    """Helper for rotation matrix along X."""
    import mathutils
    return mathutils.Matrix.Rotation(math.radians(angle_deg), 4, 'X')

def mathutils_rotation_matrix_y(angle_deg):
    """Helper for rotation matrix along Y."""
    import mathutils
    return mathutils.Matrix.Rotation(math.radians(angle_deg), 4, 'Y')

def create_hoverbike_model():
    blender_utils.reset_scene()
    import mathutils

    # ---------------------------------------------------------
    # Materials (SABLE x Capsule Corp Palette)
    # ---------------------------------------------------------
    stone_mat = blender_utils.create_stylized_material(
        'SandstoneChassis',
        color=(0.82, 0.58, 0.38, 1.0), # warm desert sandstone / terracotta
        roughness=0.8,
        metallic=0.05
    )
    dark_metal_mat = blender_utils.create_stylized_material(
        'VintageDarkMetal',
        color=(0.18, 0.16, 0.15, 1.0), # dark iron
        roughness=0.45,
        metallic=0.85
    )
    gold_mat = blender_utils.create_stylized_material(
        'AntiqueGold',
        color=(0.85, 0.65, 0.22, 1.0), # antique gold accents
        roughness=0.35,
        metallic=0.8
    )
    canopy_mat = blender_utils.create_stylized_material(
        'CircularCanopyGlass',
        color=(0.2, 0.6, 0.7, 0.45), # cyan tinted glass
        roughness=0.1,
        metallic=0.1
    )
    glow_mat = blender_utils.create_stylized_material(
        'CyanGlyphGlow',
        color=(0.1, 0.85, 0.95, 1.0), # cyan magic anti-grav glow
        roughness=0.15,
        emission_color=(0.1, 0.9, 1.0, 1.0),
        emission_strength=5.0
    )
    leather_mat = blender_utils.create_stylized_material(
        'KayakSeatLeather',
        color=(0.25, 0.15, 0.1, 1.0), # deep brown leather
        roughness=0.7,
        metallic=0.0
    )

    # ---------------------------------------------------------
    # 1. Main Capsule Body (Fuselage)
    # ---------------------------------------------------------
    fuselage_mesh = bpy.data.meshes.new('FuselageMesh')
    fuselage_obj = bpy.data.objects.new('HoverbikeCapsule', fuselage_mesh)

    bm = bmesh.new()
    # Base cylinder/cone for capsule body
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=14,
        radius1=0.95,
        radius2=0.6,
        depth=3.6
    )
    # Rotate cone to lay horizontally along Y axis
    rot_x90 = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=rot_x90, verts=bm.verts)

    # Shape capsule nose (rounded front) and tail
    for v in bm.verts:
        # Pull nose forward
        if v.co.y < -1.0:
            v.co.z *= 0.85
            v.co.x *= 0.85
        # Taper tail slightly
        if v.co.y > 1.0:
            v.co.z *= 0.9
            v.co.x *= 0.9

    bm.to_mesh(fuselage_mesh)
    bm.free()

    bpy.context.scene.collection.objects.link(fuselage_obj)
    fuselage_obj.data.materials.append(stone_mat)

    # ---------------------------------------------------------
    # 2. Integrated Circular Canopy Bubble / Roof (Capsule Corp style)
    # ---------------------------------------------------------
    canopy_mesh = bpy.data.meshes.new('CanopyMesh')
    canopy_obj = bpy.data.objects.new('CanopyBubble', canopy_mesh)

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm,
        u_segments=12,
        v_segments=8,
        radius=0.88
    )
    # Stretch dome horizontally to fit capsule roof
    scale_canopy = mathutils.Matrix.Scale(1.4, 4, (0, 1, 0)) * mathutils.Matrix.Scale(0.75, 4, (0, 0, 1))
    bmesh.ops.transform(bm, matrix=scale_canopy, verts=bm.verts)

    # Crop lower half of sphere for roof dome
    verts_to_delete = [v for v in bm.verts if v.co.z < 0.05]
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')

    bm.to_mesh(canopy_mesh)
    bm.free()

    canopy_obj.location = (0, -0.2, 0.45)
    bpy.context.scene.collection.objects.link(canopy_obj)
    canopy_obj.data.materials.append(canopy_mat)

    # Canopy Metal Rim Frame
    canopy_rim_mesh = bpy.data.meshes.new('CanopyRimMesh')
    canopy_rim_obj = bpy.data.objects.new('CanopyRimFrame', canopy_rim_mesh)

    bm = bmesh.new()
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        segments=14,
        radius=0.9
    )
    # Extrude rim ring
    res = bmesh.ops.extrude_edge_only(bm, edges=bm.edges)
    verts_ext = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
    for v in verts_ext:
        v.co.z += 0.1
    bmesh.ops.transform(bm, matrix=mathutils.Matrix.Scale(1.4, 4, (0, 1, 0)), verts=bm.verts)

    bm.to_mesh(canopy_rim_mesh)
    bm.free()

    canopy_rim_obj.location = (0, -0.2, 0.42)
    bpy.context.scene.collection.objects.link(canopy_rim_obj)
    canopy_rim_obj.data.materials.append(gold_mat)

    # ---------------------------------------------------------
    # 3. Cockpit Recumbent Kayak Seat & Controls
    # ---------------------------------------------------------
    # Kayak Bucket Seat (reclined backward)
    seat_mesh = bpy.data.meshes.new('SeatMesh')
    seat_obj = bpy.data.objects.new('KayakSeat', seat_mesh)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.7)
    # Flatten and angle seat back
    scale_seat = mathutils.Matrix.Scale(0.9, 4, (1, 0, 0)) * mathutils.Matrix.Scale(1.1, 4, (0, 1, 0)) * mathutils.Matrix.Scale(0.25, 4, (0, 0, 1))
    bmesh.ops.transform(bm, matrix=scale_seat, verts=bm.verts)

    bm.to_mesh(seat_mesh)
    bm.free()

    seat_obj.location = (0, 0.3, -0.1)
    seat_obj.rotation_euler = (math.radians(-25), 0, 0)
    bpy.context.scene.collection.objects.link(seat_obj)
    seat_obj.data.materials.append(leather_mat)

    # Steering Yoke / Control Column
    yoke_mesh = bpy.data.meshes.new('YokeMesh')
    yoke_obj = bpy.data.objects.new('YokeControls', yoke_mesh)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.04, radius2=0.04, depth=0.6)
    rot_yoke = mathutils.Matrix.Rotation(math.radians(-40), 4, 'X')
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=rot_yoke, verts=bm.verts)

    bm.to_mesh(yoke_mesh)
    bm.free()

    yoke_obj.location = (0, -0.4, 0.05)
    bpy.context.scene.collection.objects.link(yoke_obj)
    yoke_obj.data.materials.append(dark_metal_mat)

    # ---------------------------------------------------------
    # 4. Floating Side & Rear Anti-Gravity Thruster Pods
    # ---------------------------------------------------------
    def build_thruster_pod(radius=0.38, length=1.2):
        mesh = bpy.data.meshes.new('ThrusterPodMesh')
        obj = bpy.data.objects.new('ThrusterPod', mesh)
        bm = bmesh.new()

        # Stone thruster cylinder
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=radius, radius2=radius * 0.7, depth=length)
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 4, 'X'), verts=bm.verts)

        bm.to_mesh(mesh)
        bm.free()
        return obj

    # Left Thruster
    left_thruster = build_thruster_pod(radius=0.38, length=1.2)
    left_thruster.location = (-1.25, -0.2, -0.1)
    bpy.context.scene.collection.objects.link(left_thruster)
    left_thruster.data.materials.append(stone_mat)

    # Right Thruster
    right_thruster = build_thruster_pod(radius=0.38, length=1.2)
    right_thruster.location = (1.25, -0.2, -0.1)
    bpy.context.scene.collection.objects.link(right_thruster)
    right_thruster.data.materials.append(stone_mat)

    # Glowing Core Rings inside thrusters
    def build_glowing_core(radius=0.28, depth=1.25):
        mesh = bpy.data.meshes.new('GlowCoreMesh')
        obj = bpy.data.objects.new('GlowCore', mesh)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=radius, radius2=radius, depth=depth)
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 4, 'X'), verts=bm.verts)
        bm.to_mesh(mesh)
        bm.free()
        return obj

    glow_left = build_glowing_core()
    glow_left.location = (-1.25, -0.2, -0.1)
    bpy.context.scene.collection.objects.link(glow_left)
    glow_left.data.materials.append(glow_mat)

    glow_right = build_glowing_core()
    glow_right.location = (1.25, -0.2, -0.1)
    bpy.context.scene.collection.objects.link(glow_right)
    glow_right.data.materials.append(glow_mat)

    # Connecting Wing/Strut Brackets (Stone & Antique Gold)
    def build_wing_strut(x_sign=-1):
        mesh = bpy.data.meshes.new('StrutMesh')
        obj = bpy.data.objects.new('WingStrut', mesh)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=0.15)
        scale_strut = mathutils.Matrix.Scale(0.8 * x_sign, 4, (1, 0, 0)) * mathutils.Matrix.Scale(0.3, 4, (0, 1, 0)) * mathutils.Matrix.Scale(0.12, 4, (0, 0, 1))
        bmesh.ops.transform(bm, matrix=scale_strut, verts=bm.verts)
        bm.to_mesh(mesh)
        bm.free()
        return obj

    strut_l = build_wing_strut(x_sign=-1)
    strut_l.location = (-0.75, -0.2, -0.1)
    bpy.context.scene.collection.objects.link(strut_l)
    strut_l.data.materials.append(gold_mat)

    strut_r = build_wing_strut(x_sign=1)
    strut_r.location = (0.75, -0.2, -0.1)
    bpy.context.scene.collection.objects.link(strut_r)
    strut_r.data.materials.append(gold_mat)

    # Rear Main Anti-Grav Propulsion Ring (Carved Stone Ring with Glowing Cyan Glyphs)
    rear_ring_mesh = bpy.data.meshes.new('RearRingMesh')
    rear_ring_obj = bpy.data.objects.new('RearAntiGravRing', rear_ring_mesh)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.7, radius2=0.7, depth=0.25)
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 4, 'X'), verts=bm.verts)
    bm.to_mesh(rear_ring_mesh)
    bm.free()

    rear_ring_obj.location = (0, 1.75, 0.1)
    bpy.context.scene.collection.objects.link(rear_ring_obj)
    rear_ring_obj.data.materials.append(stone_mat)

    # Glowing Core for Rear Propulsion Ring
    rear_glow_mesh = bpy.data.meshes.new('RearGlowMesh')
    rear_glow_obj = bpy.data.objects.new('RearGlowCore', rear_glow_mesh)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.52, radius2=0.52, depth=0.28)
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 4, 'X'), verts=bm.verts)
    bm.to_mesh(rear_glow_mesh)
    bm.free()

    rear_glow_obj.location = (0, 1.75, 0.1)
    bpy.context.scene.collection.objects.link(rear_glow_obj)
    rear_glow_obj.data.materials.append(glow_mat)

    # ---------------------------------------------------------
    # 5. Vintage Mechanical Details & Underbody Skids
    # ---------------------------------------------------------
    # Underbody Landing Skids / Stabilization Fins
    skid_mesh = bpy.data.meshes.new('SkidMesh')
    skid_obj = bpy.data.objects.new('LandingSkid', skid_mesh)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.1)
    scale_skid = mathutils.Matrix.Scale(0.12, 4, (1, 0, 0)) * mathutils.Matrix.Scale(2.2, 4, (0, 1, 0)) * mathutils.Matrix.Scale(0.15, 4, (0, 0, 1))
    bmesh.ops.transform(bm, matrix=scale_skid, verts=bm.verts)
    bm.to_mesh(skid_mesh)
    bm.free()

    skid_obj.location = (0, 0, -0.65)
    bpy.context.scene.collection.objects.link(skid_obj)
    skid_obj.data.materials.append(dark_metal_mat)

    # Front Grille & Intake Ornaments
    grille_mesh = bpy.data.meshes.new('GrilleMesh')
    grille_obj = bpy.data.objects.new('FrontIntake', grille_mesh)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.35, radius2=0.25, depth=0.15)
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 4, 'X'), verts=bm.verts)
    bm.to_mesh(grille_mesh)
    bm.free()

    grille_obj.location = (0, -1.82, -0.05)
    bpy.context.scene.collection.objects.link(grille_obj)
    grille_obj.data.materials.append(gold_mat)

    # ---------------------------------------------------------
    # 6. Camera Setup, Environment & Render Captures
    # ---------------------------------------------------------
    # Camera Angle 1: Front 3/4 Perspective View
    blender_utils.setup_camera(location=(4.2, -5.5, 3.2), target_location=(0, 0, 0.1), lens=50)
    blender_utils.add_three_point_lighting()

    # Setup background environment color (Sable desert twilight)
    world = bpy.data.worlds.new('HoverbikeWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.07, 0.11, 1.0)
        bg_node.inputs['Strength'].default_value = 0.9

    captures_dir = "hoverbike/captures"
    os.makedirs(captures_dir, exist_ok=True)

    # Render preview snapshot 1 (Angle 1: Side/Front Perspective)
    blender_utils.configure_render(f"{captures_dir}/iteration_1_angle1.png", resolution=(800, 800))
    bpy.ops.render.render(write_still=True)
    print("Rendered hoverbike iteration_1_angle1.png")

    # Render preview snapshot 2 (Angle 2: Top/Rear Canopy & Thrusters Focus)
    cam = bpy.context.scene.camera
    cam.location = (-3.8, 4.2, 3.8)
    # Point at hoverbike center
    direction = [0 - (-3.8), 0 - 4.2, 0.1 - 3.8]
    rot_x = math.atan2(math.hypot(direction[0], direction[1]), direction[2])
    rot_z = math.atan2(direction[1], direction[0]) + math.pi / 2
    cam.rotation_euler = (rot_x, 0, rot_z)

    blender_utils.configure_render(f"{captures_dir}/iteration_1_angle2.png", resolution=(800, 800))
    bpy.ops.render.render(write_still=True)
    print("Rendered hoverbike iteration_1_angle2.png")

    # Save .blend file & export .glb
    blend_path = "hoverbike/hoverbike.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved .blend to {blend_path}")

    glb_path = "hoverbike/hoverbike.glb"
    blender_utils.export_model(glb_path)
    print(f"Exported model to {glb_path}")

if __name__ == '__main__':
    create_hoverbike_model()
