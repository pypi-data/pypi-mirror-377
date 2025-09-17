# rgb_framework/colors.py

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an RGB tuple (r, g, b) to a hex string."""
    r, g, b = rgb
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert a hex string (e.g., '#ff0000') to an RGB tuple (r, g, b)."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_grayscale(rgb: tuple[int, int, int]) -> int:
    """Convert an RGB tuple to a grayscale value using average method."""
    r, g, b = rgb
    return round((r + g + b) / 3)
