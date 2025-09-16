"""Folder model for the Templafy API."""

from pydantic import BaseModel, ConfigDict


class Folder(BaseModel):
    """A Templafy folder."""

    id: str
    name: str
    parent_id: str | None = None
    library_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(extra="allow")
