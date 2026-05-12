import os

os.environ.setdefault("FALKORDB_HOST", "localhost")
os.environ.setdefault("FALKORDB_PORT", "6380")

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def sample_topic_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def sample_course_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def topic_data(sample_topic_id) -> dict:
    return {
        "id": sample_topic_id,
        "name": "Atomic Structure",
        "slug": "atomic-structure",
        "domain": "chemistry",
        "description": "The composition of atoms.",
        "complexity": 3,
        "status": "available",
        "explanation_level": 1,
        "content_ready": False,
    }


@pytest.fixture
def mock_graph() -> MagicMock:
    return AsyncMock()
