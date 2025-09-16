from pydantic import BaseModel
from typing import Optional
from .components import COMPONENTS


class Field(BaseModel):
    """
    Represents a form field on a Page, linking a label, component, and optional form key.

    Attributes:
        label (str): Human-readable label for the field.
        component (COMPONENTS): The component associated with this field (e.g., text, image, etc.).
        form_key (Optional[str]): Optional key used to map this field in form data.
        required (Optional[bool]): Whether this field is required. Defaults to True.
    """
    label: str
    component: COMPONENTS
    form_key: Optional[str] = None
    required: Optional[bool] = True
