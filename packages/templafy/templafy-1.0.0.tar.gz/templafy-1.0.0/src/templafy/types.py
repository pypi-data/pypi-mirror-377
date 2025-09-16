"""Common type definitions for the Templafy API client."""

from typing import Any, Literal, TypeAlias

# Response types
Response: TypeAlias = dict[str, Any]
ResponseList: TypeAlias = list[dict[str, Any]]

# HTTP methods
HTTPMethod: TypeAlias = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

# File types for upload/download
FileType: TypeAlias = bytes | str
FileDict: TypeAlias = dict[str, Any]

# Common query parameters
QueryParams: TypeAlias = dict[str, str | int | bool | list[str]] | None

# Headers
Headers: TypeAlias = dict[str, str]

# JSON data
JSONType: TypeAlias = dict[str, Any] | list[Any] | str | int | float | bool | None
