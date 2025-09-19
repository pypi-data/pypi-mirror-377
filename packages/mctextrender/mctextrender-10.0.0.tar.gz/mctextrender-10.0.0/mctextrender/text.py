from PIL import Image, ImageFont, ImageDraw
from typing import Literal

from .colors import ColorMappings
from .tools import (
    get_start_point,
    calc_shadow_color,
    load_font,
    split_string
)


def render_mc_text(
    text: str,
    position: tuple[int, int],
    image: Image.Image,
    font_size: int | None = 20,
    shadow_offset: tuple[int, int] = None,
    align: Literal['left', 'center', 'right'] = 'left'
) -> int:
    """
    Render Minecraft-style formatted text onto an image.

    Supports color codes, alignment, and optional drop shadows.  
    Color codes are parsed from `ColorMappings.color_codes` and applied
    inline while rendering text segments.

    Args:
        text (str): The text string to render. May contain color codes.
        position (tuple[int, int]): The base (x, y) position for rendering.
            - For left alignment: the starting point of the text.
            - For center/right alignment: the reference point to align against.
        image (Image.Image): The PIL image to draw on.
        font_size (int | None, optional): Font size in pixels.
            Defaults to 20.
        shadow_offset (tuple[int, int], optional): (x, y) offset for a text shadow.
            If provided, a darker version of the text is rendered at this offset.
            Defaults to None.
        align (Literal['left', 'center', 'right'], optional): Text alignment mode.
            - 'left': Start at `position[0]`.
            - 'center': Center text around `position[0]`.
            - 'right': Align text to the right of `position[0]`.
            Defaults to 'left'.

    Returns:
        int: The final x-coordinate after rendering the text (end position).
    """
    font = load_font(font_size)

    split_chars = tuple(ColorMappings.color_codes)
    bits = tuple(split_string(text, split_chars))

    actual_text = ''.join([bit[0] for bit in bits])

    draw = ImageDraw.Draw(image)

    x, y = position
    x = get_start_point(
        text=actual_text,
        font=font,
        align=align,
        pos=x
    )

    for text, color_code in bits:
        color = ColorMappings.color_codes.get(color_code, ColorMappings.white)

        if shadow_offset is not None:
            off_x, off_y = shadow_offset
            shadow_color = calc_shadow_color(color)
            draw.text((x + off_x, y + off_y), text,
                      fill=shadow_color, font=font)

        draw.text((x, y), text, fill=color, font=font)
        x += int(draw.textlength(text, font=font))

    return x
