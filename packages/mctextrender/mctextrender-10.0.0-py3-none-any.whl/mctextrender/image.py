from PIL import Image, UnidentifiedImageError
from typing import Literal, TypedDict
from io import BytesIO

from .text import render_mc_text


class TextOptions(TypedDict):
    """
    Configuration options for rendering text onto an image.

    Attributes:
        font_size (int): The size of the font in pixels.
        position (tuple[int, int]): The (x, y) starting position of the text.
        shadow_offset (tuple[int, int] | None): Optional (x, y) offset for a text shadow.
            If None, no shadow is drawn.
        align (Literal["left", "right", "center"]): The alignment mode for text rendering.
    """

    font_size: int
    position: tuple[int, int]
    shadow_offset: tuple[int, int] | None
    align: Literal["left", "right", "center"]

    @staticmethod
    def default() -> 'TextOptions':
        """
        Create a default set of text rendering options.

        Returns:
            TextOptions: A dictionary with default values:
                - font_size: 16
                - position: (0, 0)
                - shadow_offset: None
                - align: "left"
        """
        return {
            "font_size": 16,
            "position": (0, 0),
            "shadow_offset": None,
            "align": "left"
        }


class ImageRender:
    """
    Utility class for manipulating and saving images.

    Provides methods to overlay images, add text, and export the
    result as a file or byte stream.
    """

    def __init__(self, base_image: Image.Image):
        """
        Initialize an ImageRender instance.

        Args:
            base_image (Image.Image): The base image to work with.
        """
        self._image: Image.Image = base_image.convert("RGBA")
        self.text = TextRender(self._image)

    def overlay_image(self, overlay_image: Image.Image) -> None:
        """
        Overlay another image on top of the base image.

        Args:
            overlay_image (Image.Image): The image to overlay, which will be
                composited with alpha blending.
        """
        self._image.alpha_composite(overlay_image.convert("RGBA"))

    def to_bytes(self) -> bytes:
        """
        Export the current image to PNG bytes.

        Returns:
            bytes: The image data encoded as PNG.
        """
        image_bytes = BytesIO()
        self._image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        return image_bytes

    def save(self, filepath: str, **kwargs) -> None:
        """
        Save the image to a file.

        Args:
            filepath (str): Path where the image will be saved.
            **kwargs: Additional arguments passed to `PIL.Image.Image.save`.
        """
        self._image.save(filepath, **kwargs)

    @property
    def size(self) -> tuple[int, int]:
        """
        Get the size of the image.

        Returns:
            tuple[int, int]: A (width, height) tuple.
        """
        return self._image.size


class TextRender:
    """
    Helper class for rendering text onto a given image.

    Uses `render_mc_text` for Minecraft-style formatted text rendering.
    """

    def __init__(self, image: Image.Image) -> None:
        """
        Initialize a TextRender instance.

        Args:
            image (Image.Image): The target image to draw text onto.
        """
        self._image = image

    def draw(
        self,
        text: str,
        text_options: TextOptions = TextOptions.default()
    ) -> None:
        """
        Draw a single line of text onto the image.

        Args:
            text (str): The text string to render.
            text_options (TextOptions, optional): Rendering options such as font size,
                position, shadow, and alignment. Defaults to TextOptions.default().
        """
        if "position" not in text_options:
            text_options["position"] = (0, 0)
        render_mc_text(text, image=self._image, **text_options)

    def draw_many(
        self,
        text_info: list[tuple[str, TextOptions]],
        default_text_options: TextOptions
    ) -> None:
        """
        Draw multiple text strings onto the image with varying options.

        Args:
            text_info (list[tuple[str, TextOptions]]): A list of (text, options) tuples.
                Each string will be drawn using the merged options.
            default_text_options (TextOptions): Base options applied to all text,
                which can be overridden by individual options.
        """
        for text, text_options in text_info:
            self.draw(
                text, {**default_text_options, **text_options}
            )
