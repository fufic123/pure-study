import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test")
os.environ.setdefault("MATERIAL_SERVICE_URL", "http://material:8004")
os.environ.setdefault("GRAPH_SERVICE_URL", "http://graph:8002")

import pytest


@pytest.fixture
def sample_topic() -> dict:
    return {
        "id": "topic-123",
        "name": "Atomic Structure",
        "slug": "atomic-structure",
        "domain": "chemistry",
        "description": "The composition of atoms.",
        "complexity": 3,
        "status": "in_progress",
        "explanation_level": 1,
        "content_ready": True,
    }


@pytest.fixture
def chat_history() -> list[dict]:
    return [
        {"role": "user", "content": "What is an atom?"},
        {"role": "assistant", "content": "An atom is the smallest unit of matter."},
    ]
