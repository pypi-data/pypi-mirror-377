from pydantic import BaseModel
from typing import Dict, Union, Tuple, Optional
from .field import Field
from .components import get_component, COMPONENTS

class PageOptions(BaseModel):
    """
    Configuration options for a Page.

    Attributes:
        name (str): The name of the page.
        width (int): Width of the page.
        height (int): Height of the page.
        background (Union[str, bytes, None]): Path to a background image or raw bytes.
        background_color (Optional[Tuple]): RGBA color for the background (default: transparent).
    """
    name: str
    width: int
    height: int
    background: Union[str, bytes, None] = None
    background_color: Optional[Tuple] = (0, 0, 0, 0)


class Page(BaseModel):
    """
    Represents a page in the model, containing fields and layout options.

    Attributes:
        options (PageOptions): Page configuration options.
        fields (Optional[Dict[str, Field]]): Dictionary of fields on the page.
    """
    options: PageOptions
    fields: Optional[Dict[str, Field]] = {}

    def to_form(self) -> dict:
        """
        Generate an empty form dictionary based on the fields that have a `form_key`.

        Returns:
            dict: Keys are `form_key`s from fields, values are empty strings.
        """
        return {field.form_key: "" for field in self.fields.values() if field.form_key}

    def add_component(self, name: str, component: str, form_key: Optional[str] = None):
        """
        Add a new component to the page.

        Args:
            name (str): The unique name of the field.
            component (str): Component type to create (resolved via `get_component`).
            form_key (Optional[str]): Optional key to map this field in forms.

        Returns:
            COMPONENTS: The newly created component instance.

        Raises:
            Exception: If a field with the same name already exists.
        """
        if name in self.fields:
            raise Exception(f"Field with name '{name}' already exists.")
        field = Field(label=name, component=get_component(component), form_key=form_key)
        self.fields[name] = field
        return field.component

    def get_component(self, name: str) -> COMPONENTS:
        """
        Retrieve a component from the page by field name.

        Args:
            name (str): The name of the field.

        Returns:
            COMPONENTS: The component associated with the field.

        Raises:
            Exception: If no field exists with the given name.
        """
        if name not in self.fields:
            raise Exception(f"No field found with name '{name}'.")
        return self.fields[name].component

    def set_width(self, width: int):
        """
        Set the width of the page.

        Args:
            width (int): The new width.

        Returns:
            self: The Page instance (for method chaining).
        """
        self.options.width = width
        return self

    def set_height(self, height: int):
        """
        Set the height of the page.

        Args:
            height (int): The new height.

        Returns:
            self: The Page instance (for method chaining).
        """
        self.options.height = height
        return self

    def set_dimension(self, width: int, height: int):
        """
        Set both width and height of the page.

        Args:
            width (int): The new width.
            height (int): The new height.

        Returns:
            self: The Page instance (for method chaining).
        """
        self.set_width(width)
        self.set_height(height)
        return self

    def set_background(self, background: Union[str, Tuple[int, int, int]]):
        """
        Set the background of the page.

        Args:
            background (Union[str, Tuple[int, int, int]]):
                - str: Path to a background image.
                - Tuple[int, int, int]: RGB background color.

        Returns:
            self: The Page instance (for method chaining).
        """
        if isinstance(background, str):
            self.options.background = background
        elif isinstance(background, Tuple):
            self.options.background_color = background
        return self
