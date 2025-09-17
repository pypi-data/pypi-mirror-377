from PIL import Image, ImageOps

def convert_to_grayscale(input_path: str, output_path: str) -> None:
    """
    Convert an image to grayscale and save it.
    
    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the grayscale image.
    """
    img = Image.open(input_path)
    gray_img = ImageOps.grayscale(img)
    gray_img.save(output_path)


def apply_color_filter(input_path: str, output_path: str, color: str) -> None:
    """
    Apply a simple color filter (red, green, blue) to an image.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the filtered image.
        color (str): One of ['red', 'green', 'blue'].
    """
    img = Image.open(input_path).convert("RGB")
    r, g, b = img.split()

    if color == "red":
        filtered_img = Image.merge("RGB", (r, r.point(lambda _: 0), r.point(lambda _: 0)))
    elif color == "green":
        filtered_img = Image.merge("RGB", (g.point(lambda _: 0), g, g.point(lambda _: 0)))
    elif color == "blue":
        filtered_img = Image.merge("RGB", (b.point(lambda _: 0), b.point(lambda _: 0), b))
    else:
        raise ValueError("Color must be one of ['red', 'green', 'blue'].")

    filtered_img.save(output_path)
