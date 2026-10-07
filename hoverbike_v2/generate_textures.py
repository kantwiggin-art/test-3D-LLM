import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

def create_watercolor_noise(width, height, base_color, noise_intensity=15):
    """Generates a soft painterly/watercolor noise background."""
    img = Image.new("RGBA", (width, height), base_color)
    pixels = img.load()

    # Generate multi-scale Perlin-like soft noise
    random.seed(42)
    r_base, g_base, b_base = base_color[:3]

    # Layer 1: Fine grain
    for y in range(height):
        for x in range(width):
            var = random.randint(-noise_intensity, noise_intensity)
            r = max(0, min(255, r_base + var))
            g = max(0, min(255, g_base + var))
            b = max(0, min(255, b_base + var))
            pixels[x, y] = (r, g, b, 255)

    # Apply soft blur to simulate watercolor blend
    img = img.filter(ImageFilter.GaussianBlur(radius=2.0))
    return img

def draw_7_pointed_star(draw, center, radius, inner_radius, outline_color, fill_color=None):
    """Draws a 7-pointed star decal on the texture."""
    points = []
    cx, cy = center
    num_points = 7
    for i in range(num_points * 2):
        r = radius if i % 2 == 0 else inner_radius
        angle = i * math.pi / num_points - math.pi / 2
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))

    if fill_color:
        draw.polygon(points, fill=fill_color)
    draw.polygon(points, outline=outline_color, width=3)

def generate_terracotta_texture(filepath="hoverbike_v2/textures/terracotta_hull.png"):
    width, height = 1024, 1024
    # SABLE Terracotta base color
    img = create_watercolor_noise(width, height, (200, 105, 75, 255), noise_intensity=20)
    draw = ImageDraw.Draw(img)

    # Draw cel-shaded panel borders and decorative line art
    panel_color = (110, 48, 30, 255)
    highlight_color = (240, 160, 130, 255)
    gold_color = (220, 170, 60, 255)
    cyan_glow = (0, 230, 255, 255)

    # Grid panel lines (SABLE aesthetic paneling)
    for y in range(0, height, 128):
        draw.line([(0, y), (width, y)], fill=panel_color, width=4)
        draw.line([(0, y + 3), (width, y + 3)], fill=highlight_color, width=2)

    for x in range(0, width, 256):
        draw.line([(x, 0), (x, height)], fill=panel_color, width=4)

    # Diagonal racing/runic stripes
    for i in range(-512, width + 512, 128):
        draw.line([(i, 0), (i + 512, height)], fill=gold_color, width=6)

    # Central 7-pointed star emblems (Decals for top hull)
    draw_7_pointed_star(draw, (256, 256), radius=80, inner_radius=35, outline_color=gold_color, fill_color=(220, 120, 80, 255))
    draw_7_pointed_star(draw, (256, 256), radius=40, inner_radius=18, outline_color=cyan_glow, fill_color=cyan_glow)

    draw_7_pointed_star(draw, (768, 768), radius=80, inner_radius=35, outline_color=gold_color, fill_color=(220, 120, 80, 255))
    draw_7_pointed_star(draw, (768, 768), radius=40, inner_radius=18, outline_color=cyan_glow, fill_color=cyan_glow)

    # Outer cel border framing
    draw.rectangle([4, 4, width-4, height-4], outline=panel_color, width=8)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)
    print(f"Saved: {filepath}")

def generate_cream_texture(filepath="hoverbike_v2/textures/cream_panel.png"):
    width, height = 1024, 1024
    # Desert cream base
    img = create_watercolor_noise(width, height, (235, 222, 198, 255), noise_intensity=15)
    draw = ImageDraw.Draw(img)

    panel_color = (150, 135, 110, 255)
    highlight_color = (255, 250, 240, 255)
    terracotta_stripe = (195, 95, 68, 255)

    # Horizontal panel lines
    for y in range(0, height, 128):
        draw.line([(0, y), (width, y)], fill=panel_color, width=3)
        draw.line([(0, y + 2), (width, y + 2)], fill=highlight_color, width=2)

    # Vertical accent stripes
    draw.rectangle([128, 0, 192, height], fill=terracotta_stripe)
    draw.rectangle([832, 0, 896, height], fill=terracotta_stripe)

    # Cel border framing
    draw.rectangle([4, 4, width-4, height-4], outline=panel_color, width=6)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)
    print(f"Saved: {filepath}")

def generate_chassis_texture(filepath="hoverbike_v2/textures/chassis_dark.png"):
    width, height = 1024, 1024
    # Dark slate bronze
    img = create_watercolor_noise(width, height, (42, 44, 52, 255), noise_intensity=12)
    draw = ImageDraw.Draw(img)

    seam_color = (20, 22, 28, 255)
    scratch_color = (70, 75, 88, 255)
    copper_rivet = (180, 110, 60, 255)

    # Metal grid plates
    for y in range(0, height, 64):
        draw.line([(0, y), (width, y)], fill=seam_color, width=3)

    for x in range(0, width, 128):
        draw.line([(x, 0), (x, height)], fill=seam_color, width=3)
        # Rivets at intersections
        for y in range(0, height, 64):
            draw.ellipse([x-4, y-4, x+4, y+4], fill=copper_rivet)

    # Random scratches
    random.seed(101)
    for _ in range(40):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = x1 + random.randint(-30, 30)
        y2 = y1 + random.randint(-30, 30)
        draw.line([(x1, y1), (x2, y2)], fill=scratch_color, width=2)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)
    print(f"Saved: {filepath}")

def generate_pilot_texture(filepath="hoverbike_v2/textures/pilot_suit.png"):
    width, height = 512, 512
    # Sand desert suit
    img = create_watercolor_noise(width, height, (210, 190, 160, 255), noise_intensity=15)
    draw = ImageDraw.Draw(img)

    leather_color = (90, 50, 30, 255)
    visor_color = (0, 230, 255, 255)

    # Leather harness straps
    draw.rectangle([0, 200, width, 240], fill=leather_color)
    draw.rectangle([200, 0, 240, height], fill=leather_color)

    # Cyan visor block
    draw.rectangle([350, 50, 480, 150], fill=visor_color)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)
    print(f"Saved: {filepath}")

if __name__ == "__main__":
    generate_terracotta_texture()
    generate_cream_texture()
    generate_chassis_texture()
    generate_pilot_texture()
