"""API endpoint modules for the Templafy API."""

# Re-export all API modules for easy importing
from . import documents, folders, images, libraries, links, slides, spaces, spreadsheets

__all__ = [
    "documents",
    "folders",
    "images",
    "libraries",
    "links",
    "slides",
    "spaces",
    "spreadsheets",
]
