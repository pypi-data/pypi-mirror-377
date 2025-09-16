"""Library model for the Templafy API."""

from pydantic import BaseModel, ConfigDict


class Library(BaseModel):
    """A Templafy library."""

    id: str
    name: str
    description: str | None = None
    space_id: str | None = None
    is_active: bool = True
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(extra="allow")
