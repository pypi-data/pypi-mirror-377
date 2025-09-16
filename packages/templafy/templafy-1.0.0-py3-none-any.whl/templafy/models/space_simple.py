"""Simple space model for the Templafy API (no external dependencies)."""

from typing import Any


class Space:
    """A Templafy space (workspace/tenant)."""

    def __init__(  # noqa: PLR0913
        self,
        space_id: str,
        name: str,
        description: str | None = None,
        *,
        is_active: bool = True,
        created_at: str | None = None,
        updated_at: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Space.

        Args:
            space_id: Space ID
            name: Space name
            description: Space description
            is_active: Whether the space is active
            created_at: Creation timestamp
            updated_at: Update timestamp
            **kwargs: Additional fields
        """
        self.id = space_id
        self.name = name
        self.description = description
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

        # Store additional fields
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Space(id='{self.id}', name='{self.name}')"
