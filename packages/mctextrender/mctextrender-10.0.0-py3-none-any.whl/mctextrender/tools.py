import re
from PIL import Image, ImageFont, ImageDraw
from importlib import resources
from typing import Literal

from .colors import ColorMappings


dummy_img = Image.new('RGBA', (0, 0))
dummy_draw = ImageDraw.Draw(dummy_img)


def split_string(
    input_string: str,
    split_chars: tuple | list
) -> list[tuple[str, str]]:
    """
    Split a string into segments based on given split characters,
    preserving the delimiter alongside each piece.

    Args:
        input_string (str): The text to be split.
        split_chars (tuple | list): Characters or substrings used as delimiters.

    Returns:
        list[tuple[str, str]]: A list of tuples where each tuple contains:
            - The text segment.
            - The delimiter that followed it (empty string if none).
    """
    pattern = '|'.join(map(re.escape, split_chars))

    match_posses = re.finditer(f"(.*?)(?:{pattern}|$)", input_string)
    matches = [match.group(1) for i, match in enumerate(match_posses) if i != 0]
    matches.remove("")

    if not matches:
        return [(input_string, '')]

    values = re.findall(pattern, input_string)

    if not input_string.startswith(tuple(split_chars)):
        values.insert(0, '')

    return list(zip(matches, values))


def load_font(font_size: int) -> dict[str, ImageFont.FreeTypeFont]:
    """
    Load the main font at a given size.

    Args:
        font_size (int): The desired font size.

    Returns:
        ImageFont.FreeTypeFont: The loaded font object.
    """
    with resources.path("mctextrender.font", "main.ttf") as font_path:
        return ImageFont.truetype(str(font_path), font_size)


def calc_shadow_color(rgb: tuple) -> tuple[int, int, int]:
    """
    Calculate a shadow color based on a given RGB value.

    The shadow color is a darker version (25%) of the original.

    Args:
        rgb (tuple): An (R, G, B) tuple representing the color.

    Returns:
        tuple[int, int, int]: A new (R, G, B) tuple for the shadow color.
    """
    return tuple([int(c * 0.25) for c in rgb])


def get_text_len(text: str, font: ImageFont.ImageFont) -> float:
    """
    Get the rendered pixel width of a text string for a given font.

    Args:
        text (str): The text to measure.
        font (ImageFont.ImageFont): The font used to render the text.

    Returns:
        float: The width of the text in pixels.
    """
    return dummy_draw.textlength(text, font=font)


def get_actual_text(text: str) -> str:
    """
    Remove color codes from a string and return only the visible text.

    Args:
        text (str): The input text containing color codes.

    Returns:
        str: The plain text with formatting codes stripped out.
    """
    split_chars = tuple(ColorMappings.color_codes)
    bits = tuple(split_string(text, split_chars))

    actual_text = ''.join([bit[0] for bit in bits])
    return actual_text


def get_start_point(
    text: str = None,
    font: ImageFont.ImageFont = None,
    align: Literal['left', 'center', 'right'] = 'left',
    pos: int = 0,
    text_len: int = None
) -> int:
    """
    Calculate the starting X position for rendering text based on alignment.

    Args:
        text (str, optional): The text string. Required if `text_len` is not provided.
        font (ImageFont.ImageFont, optional): The font used. Required if `text_len` is not provided.
        align (Literal['left', 'center', 'right'], optional): The alignment.
            - 'left' (default): Align text to the left.
            - 'center': Center-align text.
            - 'right': Align text to the right.
        pos (int, optional): The base position (e.g., center or right edge).
            Defaults to 0.
        text_len (int, optional): Precomputed text length in pixels.
            If not provided, it will be calculated using `text` and `font`.

    Returns:
        int: The computed starting X coordinate.
    """
    assert (text, font, text_len).count(None) > 0

    if text_len is None:
        text_len = get_text_len(text, font)

    if align in ('default', 'left'):
        return pos

    if align in ('center', 'middle'):
        return round(pos - text_len / 2)

    if align == 'right':
        return round(pos - text_len)

    return 0