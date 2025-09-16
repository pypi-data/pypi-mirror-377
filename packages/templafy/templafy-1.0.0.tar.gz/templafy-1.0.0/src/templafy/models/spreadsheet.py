"""Spreadsheet model for the Templafy API."""

from pydantic import BaseModel, ConfigDict


class Spreadsheet(BaseModel):
    """A Templafy spreadsheet template."""

    id: str
    name: str
    description: str | None = None
    library_id: str | None = None
    folder_id: str | None = None
    tags: list[str] | None = None
    file_size: int | None = None
    download_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(extra="allow")
