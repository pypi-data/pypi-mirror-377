"""Link model for the Templafy API."""

from pydantic import BaseModel, ConfigDict


class Link(BaseModel):
    """A Templafy link asset."""

    id: str
    name: str
    description: str | None = None
    url: str
    library_id: str | None = None
    folder_id: str | None = None
    tags: list[str] | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(extra="allow")
