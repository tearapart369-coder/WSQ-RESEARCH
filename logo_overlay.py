"""Use the supplied transparent logo in the MoviePy 1.x reel pipeline."""

from pathlib import Path

import numpy as np
from PIL import Image
from moviepy.editor import ImageClip


LOGO_PATH = Path(__file__).with_name("brand_logo.png")


def create_logo_overlay(duration, video_size=(1080, 1920)):
    """Place the unchanged logo artwork at the upper left for the whole reel."""
    width, height = video_size
    logo_width = round(width * 0.22)
    with Image.open(LOGO_PATH) as original:
        logo = original.convert("RGBA")
        logo_height = round(logo.height * logo_width / logo.width)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        pixels = np.array(logo)
    return (
        ImageClip(pixels, transparent=True)
        .set_duration(duration)
        .set_position((round(width * 0.04), round(height * 0.08)))
    )
