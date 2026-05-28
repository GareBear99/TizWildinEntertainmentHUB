"""Overlay generator — creates a 'Now Playing' image for the stream using Pillow."""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import ASSETS_DIR, BACKGROUND_IMAGE, LOGO_PATH, OVERLAY_OUTPUT, STREAM_HEIGHT, STREAM_WIDTH


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Try to load a good font, fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    try:
        return ImageFont.truetype("DejaVuSans-Bold", size)
    except Exception:
        return ImageFont.load_default()


def generate_overlay(
    title: str = "TizWildin Radio",
    artist: str = "TizWildin",
    source: str = "playlist",
) -> str:
    """Generate a Now Playing overlay image. Returns path to the image."""
    width, height = STREAM_WIDTH, STREAM_HEIGHT

    # Background
    if os.path.exists(BACKGROUND_IMAGE):
        try:
            img = Image.open(BACKGROUND_IMAGE).convert("RGB").resize((width, height))
        except Exception:
            img = Image.new("RGB", (width, height), color=(10, 11, 18))
    else:
        # Generate a dark gradient background
        img = Image.new("RGB", (width, height), color=(10, 11, 18))
        draw_bg = ImageDraw.Draw(img)
        for y in range(height):
            r = int(10 + (20 * y / height))
            g = int(11 + (18 * y / height))
            b = int(18 + (54 * y / height))
            draw_bg.line([(0, y), (width, y)], fill=(r, g, b))

    draw = ImageDraw.Draw(img)

    # Semi-transparent bottom bar for track info
    bar_height = 120
    bar_y = height - bar_height
    bar_overlay = Image.new("RGBA", (width, bar_height), (0, 0, 0, 180))
    img.paste(Image.alpha_composite(
        Image.new("RGBA", (width, bar_height), (0, 0, 0, 0)),
        bar_overlay
    ).convert("RGB"), (0, bar_y))

    # Re-create draw after paste
    draw = ImageDraw.Draw(img)

    # Logo (top-right)
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_h = 56
            logo_w = int(logo.width * (logo_h / logo.height))
            logo = logo.resize((logo_w, logo_h))
            img.paste(logo, (width - logo_w - 20, 20), logo)
        except Exception:
            pass

    # Title text
    title_font = _get_font(32)
    artist_font = _get_font(20)
    status_font = _get_font(14)

    # "Now Playing" label
    draw.text((40, bar_y + 15), "♫ NOW PLAYING", fill=(134, 239, 172), font=status_font)

    # Track title
    display_title = title[:60] + "..." if len(title) > 60 else title
    draw.text((40, bar_y + 38), display_title, fill=(255, 255, 255), font=title_font)

    # Artist
    draw.text((40, bar_y + 78), f"by {artist}", fill=(160, 166, 188), font=artist_font)

    # Source badge (top-left)
    badge_text = "📻 SUBMISSION" if source == "submission" else "🎵 TIZWILDIN RADIO"
    badge_font = _get_font(16)
    draw.text((20, 20), badge_text, fill=(108, 123, 189), font=badge_font)

    # Branding (bottom-right)
    brand_font = _get_font(12)
    draw.text((width - 280, bar_y + 90), "garebear99.github.io/TizWildinEntertainmentHUB", fill=(100, 106, 128), font=brand_font)

    # Save
    Path(OVERLAY_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    img.save(OVERLAY_OUTPUT, "PNG")
    return OVERLAY_OUTPUT


def generate_default_background() -> None:
    """Generate a default dark gradient background if none exists."""
    if os.path.exists(BACKGROUND_IMAGE):
        return
    os.makedirs(ASSETS_DIR, exist_ok=True)
    width, height = STREAM_WIDTH, STREAM_HEIGHT
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(10 + (20 * y / height))
        g = int(11 + (24 * y / height))
        b = int(18 + (54 * y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    # Add subtle accent
    for x in range(0, width, 4):
        for y in range(0, height, 4):
            if (x + y) % 80 == 0:
                draw.point((x, y), fill=(108, 123, 189))
    img.save(BACKGROUND_IMAGE, "PNG")
    print(f"[overlay] Generated default background: {BACKGROUND_IMAGE}")


if __name__ == "__main__":
    generate_default_background()
    path = generate_overlay("Test Track Title", "Test Artist", "playlist")
    print(f"Generated overlay: {path}")
