"""Tests for the Space model."""

from templafy.models.space import Space


def test_space_model_creation():
    """Test Space model can be created with required fields."""
    space_data = {
        "id": "space1",
        "name": "Test Space",
        "description": "A test space",
        "is_active": True,
    }

    space = Space(**space_data)

    assert space.id == "space1"
    assert space.name == "Test Space"
    assert space.description == "A test space"
    assert space.is_active is True


def test_space_model_with_minimal_data():
    """Test Space model with minimal required data."""
    space = Space(id="space2", name="Minimal Space")

    assert space.id == "space2"
    assert space.name == "Minimal Space"
    assert space.description is None
    assert space.is_active is True
