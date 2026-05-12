from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.onboarding_agent import OnboardingAgent


def _make_response(text: str, stop_reason: str = "end_turn") -> MagicMock:
    content = MagicMock()
    content.text = text
    content.type = "text"
    resp = MagicMock()
    resp.content = [content]
    resp.stop_reason = stop_reason
    return resp


@pytest.mark.asyncio
async def test_onboarding_returns_reply_when_interview_ongoing():
    agent = OnboardingAgent(user_id="user-1")

    with patch("app.agents.base.get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=_make_response("What subject?"))
        mock_get.return_value = mock_client

        reply = await agent.run([{"role": "user", "content": "I want to learn"}])

    assert reply == "What subject?"
    assert agent.artifacts.get("course") is None


@pytest.mark.asyncio
async def test_onboarding_artifacts_course_set_after_create_course_tool():
    """create_course tool call must populate agent.artifacts['course']."""
    tool_use_block = MagicMock()
    tool_use_block.type = "tool_use"
    tool_use_block.id = "tu_1"
    tool_use_block.name = "create_course"
    tool_use_block.input = {"name": "Chemistry", "goal": "Pass exam", "domain": "chemistry"}

    tool_response = MagicMock()
    tool_response.content = [tool_use_block]
    tool_response.stop_reason = "tool_use"

    final_response = _make_response("Your graph is ready!")

    with patch("app.agents.base.get_client") as mock_get, \
         patch("app.tools.graph_tools.GraphClient") as MockGraph:
        MockGraph.return_value.create_course = AsyncMock(
            return_value={"id": "c1", "name": "Chemistry", "goal": "Pass exam", "domain": "chemistry"}
        )
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=[tool_response, final_response])
        mock_get.return_value = mock_client

        agent = OnboardingAgent(user_id="user-1")
        await agent.run([{"role": "user", "content": "Chemistry please"}])

    assert agent.artifacts["course"]["id"] == "c1"


@pytest.mark.asyncio
async def test_onboarding_done_flag_false_without_course():
    agent = OnboardingAgent(user_id="user-1")

    with patch("app.agents.base.get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=_make_response("Tell me more."))
        mock_get.return_value = mock_client

        reply = await agent.run([{"role": "user", "content": "Hi"}])

    assert reply == "Tell me more."
    assert "course" not in agent.artifacts
