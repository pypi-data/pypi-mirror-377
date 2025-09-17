"""
RGB Framework 🎨
A simple framework for RGB color handling and image processing.
"""

from .colors import rgb_to_hex, hex_to_rgb, rgb_to_grayscale
from .images import convert_to_grayscale, apply_color_filter
from .utils import generate_random_color, validate_rgb

__all__ = [
    "rgb_to_hex",
    "hex_to_rgb",
    "rgb_to_grayscale",
    "convert_to_grayscale",
    "apply_color_filter",
    "generate_random_color",
    "validate_rgb",
]
