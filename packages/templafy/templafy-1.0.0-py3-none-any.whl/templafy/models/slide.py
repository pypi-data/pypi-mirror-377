"""Slide model for the Templafy API."""

from pydantic import BaseModel, ConfigDict


class Slide(BaseModel):
    """A Templafy slide template."""

    id: str
    name: str
    description: str | None = None
    library_id: str | None = None
    folder_id: str | None = None
    tags: list[str] | None = None
    slide_number: int | None = None
    layout_name: str | None = None
    thumbnail_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(extra="allow")
