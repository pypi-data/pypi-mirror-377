import json
from typing import TypeVar, Type

T = TypeVar("T")

class ModelPersistenceMixin:
    """
    Mixin that adds JSON export and load capabilities to a class.

    Requirements:
        - The class must have a `model_dump()` method returning a serializable dictionary.
        - The class constructor must accept `**kwargs` corresponding to the dumped keys.
    """

    def export(self, path: str, indent: int = 4, encoding: str = "utf-8") -> None:
        """
        Save the instance to a JSON file.

        Args:
            path (str): Path where the JSON will be saved.
            indent (int): Number of spaces for indentation (default: 4).
            encoding (str): File encoding (default: "utf-8").
        """
        with open(path, "w", encoding=encoding) as f:
            f.write(json.dumps(self.model_dump(), indent=indent))

    @classmethod
    def load(cls: Type[T], path: str, encoding: str = "utf-8") -> T:
        """
        Load an instance from a JSON file.

        Args:
            path (str): Path of the JSON file.
            encoding (str): File encoding (default: "utf-8").

        Returns:
            T: A new instance of the class loaded from JSON.
        """
        with open(path, "r", encoding=encoding) as f:
            data = json.load(f)
        return cls(**data)
