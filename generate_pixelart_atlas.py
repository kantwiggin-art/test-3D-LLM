#!/usr/bin/env python3
"""
generate_pixelart_atlas.py
Procedurally generates a 2D isometric pixel art sprite atlas for Hoverbike V2.
Follows a limited color palette, 2:1 isometric grid, pixel-perfect line drawing,
dithering, and 4 directional perspectives (ISO Front-Right, Rear-Right, Rear-Left, Front-Left).
Uses pure Pillow (Image / ImageDraw) without external C-extensions.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

# Directory setup
OUTPUT_DIR = "pixelart"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define Pixel Art Color Palette (Hex & RGBA)
PALETTE = {
    'BG': (0, 0, 0, 0),                       # Transparent
    'OUTLINE': (35, 25, 35, 255),              # Dark outline
    'HULL_BASE': (217, 107, 67, 255),          # Terracotta
    'HULL_LIGHT': (235, 142, 103, 255),        # Terracotta Highlight
    'HULL_SHADOW': (165, 68, 35, 255),         # Terracotta Shadow
    'CREAM_BASE': (240, 226, 205, 255),        # Cream Panel
    'CREAM_LIGHT': (255, 248, 237, 255),       # Cream Highlight
    'CREAM_SHADOW': (190, 175, 155, 255),      # Cream Shadow
    'CHASSIS_BASE': (56, 50, 56, 255),         # Dark Chassis
    'CHASSIS_LIGHT': (87, 79, 87, 255),        # Chassis Highlight
    'CHASSIS_SHADOW': (30, 25, 30, 255),       # Chassis Shadow
    'CYAN_GLOW': (0, 245, 212, 255),           # Neon Cyan Glow
    'CYAN_CORE': (200, 255, 245, 255),         # Cyan Bright Core
    'GLASS_BASE': (112, 214, 255, 180),        # Canopy Glass
    'GLASS_HL': (255, 255, 255, 220),          # Glass Glint
    'PILOT_SUIT': (180, 160, 140, 255),        # Pilot Suit
    'PILOT_VISOR': (0, 230, 200, 255),         # Pilot Visor
    'SHADOW_GROUND': (15, 10, 20, 100),       # Ground Shadow
}

FRAME_SIZE = 64  # 64x64 pixels per frame


class PixelCanvas:
    """Helper for 2D pixel-exact drawing using pure PIL Image & ImageDraw."""
    def __init__(self, size=64):
        self.size = size
        self.image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def set_pixel(self, x, y, color):
        """Set a single pixel if inside bounds."""
        if 0 <= x < self.size and 0 <= y < self.size:
            self.draw.point((x, y), fill=color)

    def draw_line(self, x0, y0, x1, y1, color):
        """Draw pixel line."""
        self.draw.line([(x0, y0), (x1, y1)], fill=color, width=1)

    def fill_rect(self, x, y, w, h, color):
        """Fill an axis-aligned rectangle."""
        self.draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)

    def fill_polygon(self, points, color, dither=False):
        """Fill a polygon. If dither is True, apply a 50% checkerboard dither pattern."""
        if len(points) < 3:
            return

        if not dither:
            self.draw.polygon(points, fill=color)
            return

        # Dithered scanline polygon fill
        ys = [p[1] for p in points]
        min_y, max_y = max(0, int(min(ys))), min(self.size - 1, int(max(ys)))

        for py in range(min_y, max_y + 1):
            nodes = []
            j = len(points) - 1
            for i in range(len(points)):
                p1_x, p1_y = points[i]
                p2_x, p2_y = points[j]
                if (p1_y < py <= p2_y) or (p2_y < py <= p1_y):
                    if p2_y != p1_y:
                        x = p1_x + (py - p1_y) / (p2_y - p1_y) * (p2_x - p1_x)
                        nodes.append(x)
                j = i
            nodes.sort()

            for k in range(0, len(nodes), 2):
                if k + 1 < len(nodes):
                    x_start = max(0, int(math.ceil(nodes[k])))
                    x_end = min(self.size - 1, int(math.floor(nodes[k+1])))
                    for px in range(x_start, x_end + 1):
                        if (px + py) % 2 == 1:
                            continue
                        self.set_pixel(px, py, color)

    def draw_polygon_outline(self, points, color):
        """Draw outline around points."""
        self.draw.polygon(points, outline=color)

    def draw_circle_glow(self, cx, cy, radius, core_color, glow_color):
        """Draw a pixelated glowing aura."""
        for r in range(radius + 2, 0, -1):
            col = glow_color if r > radius // 2 else core_color
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                px = int(cx + r * math.cos(rad))
                py = int(cy + r * math.sin(rad))
                self.set_pixel(px, py, col)

    def to_image(self):
        """Return image."""
        return self.image


def draw_ground_shadow(canvas, cx, cy, rx=22, ry=11):
    """Draws dithered oval ground shadow for floating hoverbike."""
    shadow_pts = []
    for deg in range(0, 360, 20):
        rad = math.radians(deg)
        shadow_pts.append((cx + rx * math.cos(rad), cy + ry * math.sin(rad)))
    canvas.fill_polygon(shadow_pts, PALETTE['SHADOW_GROUND'], dither=True)


def generate_frame_front_right():
    """Frame 0: ISO Front-Right (Nose facing down-right / South-East)."""
    c = PixelCanvas(64)
    # Ground shadow
    draw_ground_shadow(c, cx=32, cy=46, rx=22, ry=10)

    # Hoverbike Elevation Offset
    y_off = -6

    # 1. Dark Chassis / Anti-grav Coils (Base & Exhausts)
    chassis_poly = [
        (16, 32 + y_off), (28, 24 + y_off), (44, 30 + y_off),
        (48, 36 + y_off), (36, 42 + y_off), (20, 38 + y_off)
    ]
    c.fill_polygon(chassis_poly, PALETTE['CHASSIS_BASE'])
    c.draw_polygon_outline(chassis_poly, PALETTE['OUTLINE'])

    # Anti-grav Thruster Pods (Glow circles underneath)
    c.draw_circle_glow(22, 38 + y_off, 3, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])
    c.draw_circle_glow(42, 36 + y_off, 4, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])

    # 2. Lower Fuselages (Terracotta Shadow / Lower hull)
    lower_hull = [
        (18, 30 + y_off), (32, 22 + y_off), (52, 32 + y_off),
        (46, 39 + y_off), (28, 38 + y_off)
    ]
    c.fill_polygon(lower_hull, PALETTE['HULL_SHADOW'])

    # 3. Terracotta Main Fuselage Top
    main_hull = [
        (18, 28 + y_off), (28, 18 + y_off), (48, 26 + y_off),
        (54, 32 + y_off), (44, 37 + y_off), (26, 34 + y_off)
    ]
    c.fill_polygon(main_hull, PALETTE['HULL_BASE'])
    # Dither highlight on upper ridge
    ridge_hl = [(28, 18 + y_off), (48, 26 + y_off), (44, 29 + y_off), (28, 22 + y_off)]
    c.fill_polygon(ridge_hl, PALETTE['HULL_LIGHT'], dither=True)
    c.draw_polygon_outline(main_hull, PALETTE['OUTLINE'])

    # 4. Cream Side Panels & Winglets
    wing_right = [
        (34, 36 + y_off), (46, 42 + y_off), (44, 45 + y_off), (32, 39 + y_off)
    ]
    c.fill_polygon(wing_right, PALETTE['CREAM_BASE'])
    c.draw_polygon_outline(wing_right, PALETTE['OUTLINE'])

    panel_top = [
        (24, 24 + y_off), (34, 19 + y_off), (40, 22 + y_off), (30, 27 + y_off)
    ]
    c.fill_polygon(panel_top, PALETTE['CREAM_LIGHT'])
    c.draw_polygon_outline(panel_top, PALETTE['OUTLINE'])

    # 5. Pilot inside cockpit (Seated figure)
    c.fill_polygon([(28, 22 + y_off), (32, 20 + y_off), (32, 25 + y_off), (28, 26 + y_off)], PALETTE['PILOT_SUIT'])
    c.set_pixel(31, 21 + y_off, PALETTE['PILOT_VISOR'])
    c.set_pixel(32, 21 + y_off, PALETTE['PILOT_VISOR'])

    # 6. Glass Canopy Dome
    canopy = [
        (26, 21 + y_off), (36, 16 + y_off), (42, 21 + y_off),
        (38, 27 + y_off), (28, 26 + y_off)
    ]
    c.fill_polygon(canopy, PALETTE['GLASS_BASE'])
    c.draw_line(28, 20 + y_off, 38, 17 + y_off, PALETTE['GLASS_HL'])
    c.draw_polygon_outline(canopy, PALETTE['OUTLINE'])

    # 7. 7-Pointed Star Glyph Decal on Front Nose
    c.set_pixel(48, 30 + y_off, PALETTE['CYAN_CORE'])
    c.set_pixel(49, 30 + y_off, PALETTE['CYAN_GLOW'])
    c.set_pixel(48, 29 + y_off, PALETTE['CYAN_GLOW'])
    c.set_pixel(48, 31 + y_off, PALETTE['CYAN_GLOW'])

    # Rear Exhaust Vent (Left side, background)
    c.fill_rect(16, 28 + y_off, 3, 4, PALETTE['CHASSIS_SHADOW'])

    return c.to_image()


def generate_frame_rear_right():
    """Frame 1: ISO Rear-Right (Nose facing up-right / North-East, rear in foreground)."""
    c = PixelCanvas(64)
    draw_ground_shadow(c, cx=32, cy=46, rx=22, ry=10)
    y_off = -6

    # 1. Main Terracotta Tapering Hull
    main_hull = [
        (16, 34 + y_off), (26, 38 + y_off), (48, 26 + y_off),
        (42, 18 + y_off), (22, 24 + y_off)
    ]
    c.fill_polygon(main_hull, PALETTE['HULL_BASE'])
    c.draw_polygon_outline(main_hull, PALETTE['OUTLINE'])

    # 2. Glowing Dual Exhaust Ports (Foreground Rear)
    c.draw_circle_glow(18, 34 + y_off, 4, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])
    c.draw_circle_glow(26, 38 + y_off, 4, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])

    # Rear Engine Housing
    engine_blk = [(14, 31 + y_off), (28, 38 + y_off), (26, 42 + y_off), (12, 35 + y_off)]
    c.fill_polygon(engine_blk, PALETTE['CHASSIS_BASE'])
    c.draw_polygon_outline(engine_blk, PALETTE['OUTLINE'])

    # 3. Cream Right Side Panel & Winglet
    wing = [(28, 36 + y_off), (44, 42 + y_off), (46, 39 + y_off), (30, 33 + y_off)]
    c.fill_polygon(wing, PALETTE['CREAM_BASE'])
    c.draw_polygon_outline(wing, PALETTE['OUTLINE'])

    # 4. Glass Canopy (Visible in middle background)
    canopy = [(30, 22 + y_off), (38, 18 + y_off), (44, 21 + y_off), (36, 26 + y_off)]
    c.fill_polygon(canopy, PALETTE['GLASS_BASE'])
    c.draw_polygon_outline(canopy, PALETTE['OUTLINE'])

    return c.to_image()


def generate_frame_rear_left():
    """Frame 2: ISO Rear-Left (Nose facing up-left / North-West)."""
    c = PixelCanvas(64)
    draw_ground_shadow(c, cx=32, cy=46, rx=22, ry=10)
    y_off = -6

    # 1. Main Terracotta Hull
    main_hull = [
        (48, 34 + y_off), (38, 38 + y_off), (16, 26 + y_off),
        (22, 18 + y_off), (42, 24 + y_off)
    ]
    c.fill_polygon(main_hull, PALETTE['HULL_BASE'])
    c.draw_polygon_outline(main_hull, PALETTE['OUTLINE'])

    # 2. Glowing Dual Exhaust Ports
    c.draw_circle_glow(46, 34 + y_off, 4, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])
    c.draw_circle_glow(38, 38 + y_off, 4, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])

    engine_blk = [(50, 31 + y_off), (36, 38 + y_off), (38, 42 + y_off), (52, 35 + y_off)]
    c.fill_polygon(engine_blk, PALETTE['CHASSIS_BASE'])
    c.draw_polygon_outline(engine_blk, PALETTE['OUTLINE'])

    # 3. Cream Left Winglet
    wing = [(36, 36 + y_off), (20, 42 + y_off), (18, 39 + y_off), (34, 33 + y_off)]
    c.fill_polygon(wing, PALETTE['CREAM_BASE'])
    c.draw_polygon_outline(wing, PALETTE['OUTLINE'])

    # 4. Glass Canopy
    canopy = [(34, 22 + y_off), (26, 18 + y_off), (20, 21 + y_off), (28, 26 + y_off)]
    c.fill_polygon(canopy, PALETTE['GLASS_BASE'])
    c.draw_polygon_outline(canopy, PALETTE['OUTLINE'])

    return c.to_image()


def generate_frame_front_left():
    """Frame 3: ISO Front-Left (Nose facing down-left / South-West)."""
    c = PixelCanvas(64)
    draw_ground_shadow(c, cx=32, cy=46, rx=22, ry=10)
    y_off = -6

    # 1. Chassis Base & Anti-grav Pods
    chassis_poly = [
        (48, 32 + y_off), (36, 24 + y_off), (20, 30 + y_off),
        (16, 36 + y_off), (28, 42 + y_off), (44, 38 + y_off)
    ]
    c.fill_polygon(chassis_poly, PALETTE['CHASSIS_BASE'])
    c.draw_polygon_outline(chassis_poly, PALETTE['OUTLINE'])

    c.draw_circle_glow(42, 38 + y_off, 3, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])
    c.draw_circle_glow(22, 36 + y_off, 4, PALETTE['CYAN_CORE'], PALETTE['CYAN_GLOW'])

    # 2. Terracotta Main Hull
    main_hull = [
        (46, 28 + y_off), (36, 18 + y_off), (16, 26 + y_off),
        (10, 32 + y_off), (20, 37 + y_off), (38, 34 + y_off)
    ]
    c.fill_polygon(main_hull, PALETTE['HULL_BASE'])
    ridge_hl = [(36, 18 + y_off), (16, 26 + y_off), (20, 29 + y_off), (36, 22 + y_off)]
    c.fill_polygon(ridge_hl, PALETTE['HULL_LIGHT'], dither=True)
    c.draw_polygon_outline(main_hull, PALETTE['OUTLINE'])

    # 3. Cream Side Panel & Left Winglet
    wing_left = [
        (30, 36 + y_off), (18, 42 + y_off), (20, 45 + y_off), (32, 39 + y_off)
    ]
    c.fill_polygon(wing_left, PALETTE['CREAM_BASE'])
    c.draw_polygon_outline(wing_left, PALETTE['OUTLINE'])

    panel_top = [
        (40, 24 + y_off), (30, 19 + y_off), (24, 22 + y_off), (34, 27 + y_off)
    ]
    c.fill_polygon(panel_top, PALETTE['CREAM_LIGHT'])
    c.draw_polygon_outline(panel_top, PALETTE['OUTLINE'])

    # 4. Pilot inside cockpit
    c.fill_polygon([(36, 22 + y_off), (32, 20 + y_off), (32, 25 + y_off), (36, 26 + y_off)], PALETTE['PILOT_SUIT'])
    c.set_pixel(33, 21 + y_off, PALETTE['PILOT_VISOR'])
    c.set_pixel(32, 21 + y_off, PALETTE['PILOT_VISOR'])

    # 5. Glass Canopy
    canopy = [
        (38, 21 + y_off), (28, 16 + y_off), (22, 21 + y_off),
        (26, 27 + y_off), (36, 26 + y_off)
    ]
    c.fill_polygon(canopy, PALETTE['GLASS_BASE'])
    c.draw_line(36, 20 + y_off, 26, 17 + y_off, PALETTE['GLASS_HL'])
    c.draw_polygon_outline(canopy, PALETTE['OUTLINE'])

    # 6. Star Glyph Decal on Front Nose
    c.set_pixel(16, 30 + y_off, PALETTE['CYAN_CORE'])
    c.set_pixel(15, 30 + y_off, PALETTE['CYAN_GLOW'])
    c.set_pixel(16, 29 + y_off, PALETTE['CYAN_GLOW'])
    c.set_pixel(16, 31 + y_off, PALETTE['CYAN_GLOW'])

    return c.to_image()


def build_sprite_atlas():
    """Assembles all 4 isometric direction frames into a single sprite atlas grid."""
    frames = [
        ("ISO 0° Front-Right", generate_frame_front_right()),
        ("ISO 90° Rear-Right", generate_frame_rear_right()),
        ("ISO 180° Rear-Left", generate_frame_rear_left()),
        ("ISO 270° Front-Left", generate_frame_front_left()),
    ]

    # Save individual frames for inspection
    for idx, (label, img) in enumerate(frames):
        img.save(os.path.join(OUTPUT_DIR, f"frame_{idx}.png"))

    # Create 2x2 Sprite Atlas Grid
    atlas_w = FRAME_SIZE * 2 + 16
    atlas_h = FRAME_SIZE * 2 + 32
    atlas = Image.new("RGBA", (atlas_w, atlas_h), (20, 18, 24, 255))
    draw = ImageDraw.Draw(atlas)

    positions = [
        (8, 8),                       # Top-Left (0°)
        (8 + FRAME_SIZE + 8, 8),       # Top-Right (90°)
        (8, 8 + FRAME_SIZE + 16),      # Bottom-Left (180°)
        (8 + FRAME_SIZE + 8, 8 + FRAME_SIZE + 16) # Bottom-Right (270°)
    ]

    for idx, (label, img) in enumerate(frames):
        pos = positions[idx]
        # Draw dark border box around frame
        draw.rectangle([pos[0]-1, pos[1]-1, pos[0]+FRAME_SIZE, pos[1]+FRAME_SIZE], outline=(60, 50, 70, 255))
        atlas.paste(img, pos, img)
        # Add small text label below
        draw.text((pos[0], pos[1] + FRAME_SIZE + 2), label.split()[0], fill=(200, 190, 210, 255))

    atlas_path = os.path.join(OUTPUT_DIR, "hoverbike_isometric_atlas.png")
    atlas.save(atlas_path)

    # Scale up version 4x for high-visibility visual inspection
    atlas_scaled = atlas.resize((atlas_w * 4, atlas_h * 4), Image.NEAREST)
    atlas_scaled_path = os.path.join(OUTPUT_DIR, "hoverbike_isometric_atlas_4x.png")
    atlas_scaled.save(atlas_scaled_path)

    print(f"Generated pixel art sprite atlas at {atlas_path} and {atlas_scaled_path}")
    return atlas_scaled_path


if __name__ == "__main__":
    build_sprite_atlas()
