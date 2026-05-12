from unittest.mock import AsyncMock, patch

import pytest
from app.services.graph_service import GraphService
from fastapi import HTTPException


@pytest.fixture
def svc(mock_graph) -> GraphService:
    return GraphService(mock_graph)


# ── open_topic ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_open_topic_transitions_to_in_progress(svc, topic_data):
    with patch.object(svc.topics, "get", AsyncMock(return_value=topic_data)), \
         patch.object(svc.topics, "update_status", AsyncMock()) as mock_update:
        result = await svc.open_topic(topic_data["id"])

        assert result["status"] == "in_progress"
        mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_open_topic_not_found_raises_404(svc):
    with patch.object(svc.topics, "get", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await svc.open_topic("nonexistent")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_open_locked_topic_raises_409(svc, topic_data):
    locked = {**topic_data, "status": "locked"}
    with patch.object(svc.topics, "get", AsyncMock(return_value=locked)):
        with pytest.raises(HTTPException) as exc:
            await svc.open_topic(locked["id"])
        assert exc.value.status_code == 409


# ── master_topic ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_master_topic_unlocks_dependents(svc, topic_data):
    in_progress = {**topic_data, "status": "in_progress"}
    dependent_id = "dep-topic-id"

    with patch.object(svc.topics, "get", AsyncMock(return_value=in_progress)), \
         patch.object(svc.topics, "update_status", AsyncMock()) as mock_update, \
         patch.object(svc.topics, "find_newly_unlockable", AsyncMock(return_value=[dependent_id])):
        result = await svc.master_topic(in_progress["id"])

        assert result["status"] == "mastered"
        assert dependent_id in result["unlocked"]
        # Called once for mastered topic + once for each dependent
        assert mock_update.call_count == 2


@pytest.mark.asyncio
async def test_master_available_topic_raises_409(svc, topic_data):
    with patch.object(svc.topics, "get", AsyncMock(return_value=topic_data)):
        with pytest.raises(HTTPException) as exc:
            await svc.master_topic(topic_data["id"])
        assert exc.value.status_code == 409


# ── escalate_explanation ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_escalate_explanation_increments_level(svc, topic_data):
    with patch.object(svc.topics, "get", AsyncMock(return_value=topic_data)), \
         patch.object(svc.topics, "update_explanation_level", AsyncMock()) as mock_update:
        result = await svc.escalate_explanation(topic_data["id"])

        assert result["explanation_level"] == 2
        mock_update.assert_called_once_with(topic_data["id"], 2)


@pytest.mark.asyncio
async def test_escalate_at_max_level_raises_409(svc, topic_data):
    maxed = {**topic_data, "explanation_level": 3}
    with patch.object(svc.topics, "get", AsyncMock(return_value=maxed)):
        with pytest.raises(HTTPException) as exc:
            await svc.escalate_explanation(maxed["id"])
        assert exc.value.status_code == 409


# ── create_edge ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_invalid_edge_type_raises_400(svc):
    with patch.object(svc.edges, "create", AsyncMock(side_effect=ValueError("Invalid edge type"))):
        with pytest.raises(HTTPException) as exc:
            await svc.create_edge("a", "b", "INVALID")
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_valid_edge_succeeds(svc):
    with patch.object(svc.edges, "create", AsyncMock()) as mock_create:
        await svc.create_edge("a", "b", "REQUIRES")
        mock_create.assert_called_once_with("a", "b", "REQUIRES")


# ── get_course ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_course_not_found_raises_404(svc):
    with patch.object(svc.courses, "get", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await svc.get_course("missing")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_course_returns_topics(svc, sample_course_id, topic_data):
    course = {"id": sample_course_id, "name": "Chemistry", "goal": "Learn it", "domain": "chemistry"}
    with patch.object(svc.courses, "get", AsyncMock(return_value=course)), \
         patch.object(svc.topics, "list_by_course", AsyncMock(return_value=[topic_data])):
        result = await svc.get_course(sample_course_id)

        assert result["id"] == sample_course_id
        assert len(result["topics"]) == 1
