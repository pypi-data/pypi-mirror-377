from pydantic import BaseModel
from typing import Tuple, Optional, Union, Dict, Callable

class Img(BaseModel):
    """
    Represents an image component that can be placed on a page.

    Attributes:
        position (Tuple[int, int]): Top-left coordinates of the image (x, y). Default is (0, 0).
        dimension (Tuple[int, int]): Width and height of the image. Default is (100, 100).
        path (Optional[str]): File path of the image. Default is None.
    """

    position: Tuple[int, int] = (0, 0)
    dimension: Tuple[int, int] = (100, 100)
    path: Optional[str] = None

    # Getters
    def get_position(self) -> Tuple[int, int]:
        """Return the (x, y) position of the image."""
        return self.position

    def get_dimension(self) -> Tuple[int, int]:
        """Return the (width, height) of the image."""
        return self.dimension

    def get_path(self) -> Optional[str]:
        """Return the file path of the image."""
        return self.path

    # Setters
    def set_position(self, value: Tuple[int, int]):
        """Set the position (x, y) of the image."""
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("position must be a tuple (x, y)")
        if not all(isinstance(v, int) for v in value):
            raise ValueError("position values must be integers")
        self.position = value
        return self

    def set_dimension(self, value: Tuple[int, int]):
        """Set the dimension (width, height) of the image."""
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("dimension must be a tuple (width, height)")
        if not all(isinstance(v, int) and v >= 0 for v in value):
            raise ValueError("dimension values must be non-negative integers")
        self.dimension = value
        return self

    def set_path(self, value: Optional[str]):
        """Set the file path of the image."""
        self.path = value
        return self

    def set_value(self, value: Optional[str]):
        """Alias for `set_path`; sets the image file path."""
        self.path = value
        return self


class Text(BaseModel):
    """
    Represents a text component that can be placed on a page.

    Attributes:
        color (Tuple[int, int, int]): RGB color of the text. Default is black (0, 0, 0).
        size (int): Font size of the text. Default is 12.
        position (Tuple[int, int]): Top-left coordinates of the text (x, y). Default is (0, 0).
        value (str): Text content. Default is empty string.
        dimension_r (int): Optional width for right-alignment or centering. Default is 0.
        font (Optional[str]): File path to a TrueType font. Default is None.
    """

    color: Tuple[int, int, int] = (0, 0, 0)
    size: int = 12
    position: Tuple[int, int] = (0, 0)
    value: str = ""
    dimension_r: int = 0
    font: Optional[str] = None

    # Getters
    def get_color(self) -> Tuple[int, int, int]:
        return self.color

    def get_size(self) -> int:
        return self.size

    def get_position(self) -> Tuple[int, int]:
        return self.position

    def get_value(self) -> str:
        return self.value

    def get_dimension_r(self) -> int:
        return self.dimension_r

    def get_font(self) -> Optional[str]:
        return self.font

    # Setters
    def set_color(self, value: Tuple[int, int, int]):
        if not isinstance(value, tuple) or len(value) != 3:
            raise ValueError("color must be a tuple (R, G, B)")
        if any(not (0 <= c <= 255) for c in value):
            raise ValueError("each color component must be between 0 and 255")
        self.color = value
        return self

    def set_size(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("size must be a positive integer")
        self.size = value
        return self

    def set_position(self, value: Tuple[int, int]):
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("position must be a tuple (x, y)")
        if not all(isinstance(v, int) for v in value):
            raise ValueError("position values must be integers")
        self.position = value
        return self

    def set_value(self, text: Optional[str]):
        if text is not None and not isinstance(text, str):
            raise ValueError("value must be a string or None")
        self.value = text
        return self

    def set_dimension_r(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError("dimension_r must be an integer >= 0")
        self.dimension_r = value
        return self

    def set_font(self, path: str):
        self.font = path
        return self


COMPONENTS = Union[Text, Img]
"""
Type alias for supported components. Can be either Text or Img.
"""

MAPPING_COMPONENTS: Dict[str, Callable[[], COMPONENTS]] = {
    "text": lambda: Text(),
    "img": lambda: Img(),
}
"""
Mapping from string component names to their factory functions.
"""

def get_component(name: str) -> COMPONENTS:
    """
    Factory function to create a new component instance by name.

    Args:
        name (str): Name of the component ("text" or "img").

    Returns:
        COMPONENTS: A new instance of the requested component.

    Raises:
        ValueError: If the component name is not found.
    """
    factory = MAPPING_COMPONENTS.get(name)
    if not factory:
        raise ValueError(f"Component '{name}' not found")
    return factory()
