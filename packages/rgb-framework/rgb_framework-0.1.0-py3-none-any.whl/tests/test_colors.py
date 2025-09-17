from rgb_framework.colors import rgb_to_hex, hex_to_rgb, rgb_to_grayscale

def test_rgb_to_hex():
    assert rgb_to_hex((255, 0, 0)) == "#ff0000"

def test_hex_to_rgb():
    assert hex_to_rgb("#00ff00") == (0, 255, 0)

def test_rgb_to_grayscale():
    assert rgb_to_grayscale((100, 150, 200)) in (149, 150)
