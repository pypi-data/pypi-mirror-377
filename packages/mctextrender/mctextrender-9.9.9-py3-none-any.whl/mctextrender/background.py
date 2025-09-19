from PIL import Image


class BackgroundImageLoader:
    """
    Utility class for loading background images.

    Provides a simple wrapper around PIL's `Image.open`, with an internal
    loader method and a public method that returns a copy of the image
    to avoid issues with file locks.
    """

    def __init__(self, path: str) -> None:
        """
        Initialize a background image loader.

        Args:
            path (str): The default path to the background image.
        """
        self._path = path

    def __load_image(self, path: str) -> Image.Image:
        """
        Load an image from a file path without copying.

        This is an internal helper method. The caller is responsible
        for handling file locks or modifications to the loaded image.

        Args:
            path (str): Path to the image file.

        Returns:
            Image.Image: The loaded PIL image.
        """
        return Image.open(path)

    def load_image(self, path: str) -> Image.Image:
        """
        Load an image from a file path and return a copy.

        Unlike `__load_image`, this method ensures the returned image is
        detached from the file, preventing file lock issues.

        Args:
            path (str): Path to the image file.

        Returns:
            Image.Image: A copy of the loaded PIL image.
        """
        return self.__load_image(path).copy()
