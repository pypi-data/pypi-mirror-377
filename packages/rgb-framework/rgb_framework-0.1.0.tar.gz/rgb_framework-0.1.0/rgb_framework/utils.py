import random


def generate_random_color():
    """Generate a random RGB color as a tuple."""
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def validate_rgb(r, g, b):
    """Validate if values are within RGB range (0-255)."""
    for val in (r, g, b):
        if not (0 <= val <= 255):
            return False
    return True
