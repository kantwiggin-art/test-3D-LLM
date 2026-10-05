import sys
import os
import math
import bmesh

# Add root folder to sys.path to import blender_utils
sys.path.append(os.path.abspath("."))
import blender_utils

import bpy

def build_star_7_mesh(outer_radius=1.2, inner_radius=0.5, depth=0.15):
    """Generates a 7-pointed star mesh curve/mesh profile."""
    mesh = bpy.data.meshes.new('Star7Mesh')
    obj = bpy.data.objects.new('Star7', mesh)

    bm = bmesh.new()
    num_points = 7
    top_verts = []
    bot_verts = []

    for i in range(num_points * 2):
        angle = i * math.pi / num_points
        r = outer_radius if i % 2 == 0 else inner_radius
        x = r * math.cos(angle)
        y = r * math.sin(angle)

        top_verts.append(bm.verts.new((x, y, depth / 2)))
        bot_verts.append(bm.verts.new((x, y, -depth / 2)))

    bm.verts.ensure_lookup_table()

    # Create top face and bottom face
    bm.faces.new(top_verts)
    bm.faces.new(reversed(bot_verts))

    # Create side faces
    n = len(top_verts)
    for i in range(n):
        i_next = (i + 1) % n
        bm.faces.new([top_verts[i], top_verts[i_next], bot_verts[i_next], bot_verts[i]])

    bm.to_mesh(mesh)
    bm.free()
    return obj

def build_notched_medallion(radius=2.0, thickness=0.4, num_notches=14, notch_depth=0.15):
    """Builds a low-poly medallion disc with notches along the outer rim."""
    mesh = bpy.data.meshes.new('MedallionMesh')
    obj = bpy.data.objects.new('Medallion', mesh)

    bm = bmesh.new()
    total_segments = num_notches * 2
    top_verts = []
    bot_verts = []

    for i in range(total_segments):
        angle = i * 2 * math.pi / total_segments
        # Alternate between full radius and notched radius
        r = radius - notch_depth if (i % 2 == 1) else radius
        x = r * math.cos(angle)
        y = r * math.sin(angle)

        top_verts.append(bm.verts.new((x, y, thickness / 2)))
        bot_verts.append(bm.verts.new((x, y, -thickness / 2)))

    bm.verts.ensure_lookup_table()

    # Fill cap faces
    bm.faces.new(top_verts)
    bm.faces.new(reversed(bot_verts))

    # Fill side faces
    n = len(top_verts)
    for i in range(n):
        i_next = (i + 1) % n
        bm.faces.new([top_verts[i], top_verts[i_next], bot_verts[i_next], bot_verts[i]])

    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_concentric_ring(inner_r, outer_r, thickness):
    """Creates a decorative concentric ring mesh."""
    mesh = bpy.data.meshes.new('RingMesh')
    obj = bpy.data.objects.new('Ring', mesh)

    bm = bmesh.new()
    segments = 28
    top_inner, top_outer, bot_inner, bot_outer = [], [], [], []

    for i in range(segments):
        angle = i * 2 * math.pi / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        top_inner.append(bm.verts.new((inner_r * cos_a, inner_r * sin_a, thickness / 2)))
        top_outer.append(bm.verts.new((outer_r * cos_a, outer_r * sin_a, thickness / 2)))
        bot_inner.append(bm.verts.new((inner_r * cos_a, inner_r * sin_a, -thickness / 2)))
        bot_outer.append(bm.verts.new((outer_r * cos_a, outer_r * sin_a, -thickness / 2)))

    bm.verts.ensure_lookup_table()

    for i in range(segments):
        i_next = (i + 1) % segments
        # Top ring face
        bm.faces.new([top_inner[i], top_outer[i], top_outer[i_next], top_inner[i_next]])
        # Bottom ring face
        bm.faces.new([bot_inner[i], bot_inner[i_next], bot_outer[i_next], bot_outer[i]])
        # Outer wall
        bm.faces.new([top_outer[i], bot_outer[i], bot_outer[i_next], top_outer[i_next]])
        # Inner wall
        bm.faces.new([top_inner[i], top_inner[i_next], bot_inner[i_next], bot_inner[i]])

    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_ancient_rune(x, y, z, size=0.12):
    """Creates a small diamond/rune ornament for the medallion surface."""
    mesh = bpy.data.meshes.new('RuneMesh')
    obj = bpy.data.objects.new('Rune', mesh)

    bm = bmesh.new()
    v1 = bm.verts.new((x, y + size, z))
    v2 = bm.verts.new((x + size * 0.7, y, z))
    v3 = bm.verts.new((x, y - size, z))
    v4 = bm.verts.new((x - size * 0.7, y, z))
    v_top = bm.verts.new((x, y, z + size * 0.6))

    bm.faces.new([v1, v2, v_top])
    bm.faces.new([v2, v3, v_top])
    bm.faces.new([v3, v4, v_top])
    bm.faces.new([v4, v1, v_top])

    bm.to_mesh(mesh)
    bm.free()
    return obj

def generate_mystic_token():
    blender_utils.reset_scene()

    # 1. Create Base Notched Medallion
    medallion = build_notched_medallion(radius=2.2, thickness=0.45, num_notches=14, notch_depth=0.15)
    bpy.context.scene.collection.objects.link(medallion)

    # Materials (SABLE / Chants of Sennaar warm sand stone + cyan glowing glyphs + antique gold)
    stone_mat = blender_utils.create_stylized_material(
        'MysticStone',
        color=(0.35, 0.28, 0.24, 1.0), # warm terracota/sandstone
        roughness=0.85,
        metallic=0.05
    )
    gold_mat = blender_utils.create_stylized_material(
        'AntiqueGold',
        color=(0.82, 0.62, 0.22, 1.0), # warm antique gold
        roughness=0.35,
        metallic=0.75
    )
    glyph_glow_mat = blender_utils.create_stylized_material(
        'CyanGlyphGlow',
        color=(0.1, 0.85, 0.9, 1.0), # cyan magic glow
        roughness=0.2,
        emission_color=(0.1, 0.9, 1.0, 1.0),
        emission_strength=4.5
    )

    medallion.data.materials.append(stone_mat)

    # 2. Add Inner Gold Rim
    ring = create_concentric_ring(inner_r=1.75, outer_r=1.95, thickness=0.5)
    bpy.context.scene.collection.objects.link(ring)
    ring.data.materials.append(gold_mat)

    # 3. Add Center Engraved 7-Pointed Star
    star = build_star_7_mesh(outer_radius=1.35, inner_radius=0.55, depth=0.2)
    star.location.z = 0.15 # Inset/engraved into top face
    bpy.context.scene.collection.objects.link(star)
    star.data.materials.append(glyph_glow_mat)

    # Boolean Difference to engrave the star into medallion (or place as inlaid glowing glyph)
    # Using glowing inlaid star for strong stylized aesthetic

    # 4. Add Decorative Surrounding Runes / Ancient Dots
    num_runes = 7
    for i in range(num_runes):
        angle = i * 2 * math.pi / num_runes + (math.pi / 7)
        rx = 1.55 * math.cos(angle)
        ry = 1.55 * math.sin(angle)
        rune = create_ancient_rune(rx, ry, z=0.23, size=0.1)
        bpy.context.scene.collection.objects.link(rune)
        rune.data.materials.append(gold_mat)

    # Additional Outer Decorative Accents (Small glowing dots)
    for i in range(14):
        angle = i * 2 * math.pi / 14
        dx = 1.85 * math.cos(angle)
        dy = 1.85 * math.sin(angle)
        dot = create_ancient_rune(dx, dy, z=0.25, size=0.05)
        bpy.context.scene.collection.objects.link(dot)
        dot.data.materials.append(glyph_glow_mat)

    # 5. Setup Camera & Lighting
    blender_utils.setup_camera(location=(0, -4.5, 4.2), target_location=(0, 0, 0), lens=55)
    blender_utils.add_three_point_lighting()

    # Setup background environment color (mysterious dark teal/sable desert night)
    world = bpy.data.worlds.new('MysticWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.04, 0.06, 0.09, 1.0)
        bg_node.inputs['Strength'].default_value = 0.8

    # Ensure output captures folder exists
    captures_dir = "mystic_token/captures"
    os.makedirs(captures_dir, exist_ok=True)

    # Render preview snapshot 1
    blender_utils.configure_render(f"{captures_dir}/iteration_1_angle1.png", resolution=(800, 800))
    bpy.ops.render.render(write_still=True)
    print("Rendered iteration_1_angle1.png")

    # Change camera angle for second preview snapshot
    cam = bpy.context.scene.camera
    cam.location = (3.2, -3.2, 3.5)
    # Re-orient camera
    direction = [-3.2, 3.2, -3.5]
    rot_x = math.atan2(math.hypot(direction[0], direction[1]), direction[2])
    rot_z = math.atan2(direction[1], direction[0]) + math.pi / 2
    cam.rotation_euler = (rot_x, 0, rot_z)

    blender_utils.configure_render(f"{captures_dir}/iteration_1_angle2.png", resolution=(800, 800))
    bpy.ops.render.render(write_still=True)
    print("Rendered iteration_1_angle2.png")

    # Save .blend file and export model
    blend_path = "mystic_token/mystic_token.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved .blend to {blend_path}")

    glb_path = "mystic_token/mystic_token.glb"
    blender_utils.export_model(glb_path)
    print(f"Exported model to {glb_path}")

if __name__ == '__main__':
    generate_mystic_token()
