"""Models for the Templafy API."""

from typing import Any

# For now use simple models without pydantic to avoid dependency issues
# during development
from .space_simple import Space


# Create simple placeholder classes for other models
class Document:
    """A Templafy document template."""

    def __init__(self, document_id: str, name: str, **kwargs: Any) -> None:
        """Initialize a Document."""
        self.id = document_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


class Library:
    """A Templafy library."""

    def __init__(self, library_id: str, name: str, **kwargs: Any) -> None:
        """Initialize a Library."""
        self.id = library_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


class Folder:
    """A Templafy folder."""

    def __init__(self, folder_id: str, name: str, **kwargs: Any) -> None:
        """Initialize a Folder."""
        self.id = folder_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


class Image:
    """A Templafy image asset."""

    def __init__(self, image_id: str, name: str, **kwargs: Any) -> None:
        """Initialize an Image."""
        self.id = image_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


class Slide:
    """A Templafy slide template."""

    def __init__(self, slide_id: str, name: str, **kwargs: Any) -> None:
        """Initialize a Slide."""
        self.id = slide_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


class Spreadsheet:
    """A Templafy spreadsheet template."""

    def __init__(self, spreadsheet_id: str, name: str, **kwargs: Any) -> None:
        """Initialize a Spreadsheet."""
        self.id = spreadsheet_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


class Link:
    """A Templafy link asset."""

    def __init__(self, link_id: str, name: str, **kwargs: Any) -> None:
        """Initialize a Link."""
        self.id = link_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)


__all__ = [
    "Document",
    "Folder",
    "Image",
    "Library",
    "Link",
    "Slide",
    "Space",
    "Spreadsheet",
]
