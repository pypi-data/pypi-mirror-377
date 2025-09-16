from pydantic import BaseModel
from typing import Dict, Optional
from .page import Page, PageOptions
from .builder import BuilderMixin
from .persistence import ModelPersistenceMixin


class Model(
    BaseModel, # 
    BuilderMixin, # Funções de builder
    ModelPersistenceMixin # Funções de Persistencia
    ):
    name: str
    pages: Optional[Dict[str, Page]] = {}

    @classmethod
    def new(cls, name: str):
        """
        Create a new instance of the class with only a name.

        Args:
            name (str): The name to assign to the new instance.

        Returns:
            cls: A new instance of the class with the given name.
        """
        return cls(name=name)

    def new_page(self, name: str) -> Page:
        """
        Create a new page with the given name and add it to the parent's page list.

        Args:
            name (str): The name of the new page.

        Returns:
            Page: The newly created Page object.

        Raises:
            Exception: If a page with the same name already exists.
        """
        page = Page(options=PageOptions(
            name=name,
            width=0,
            height=0,
        ))
        if name in self.pages:
            raise Exception("A page with this name already exists.")
        self.pages[name] = page
        return page

    def get_form(self) -> Dict:
        """
        Combine all page forms into a single dictionary.

        Returns:
            Dict: Merged form data from all pages.
        """
        merged_form = {}
        for page in self.pages.values():
            merged_form.update(page.to_form())
        return merged_form
    
    def get_schema(self) -> Dict:
        """
        Return a dictionary mapping page names to their form dictionaries.

        Returns:
            Dict: {page_name: page.to_form(), ...}
        """
        return {page_name: page.to_form() for page_name, page in self.pages.items()}
