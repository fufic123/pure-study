from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.copilot_agent import CopilotAgent


def _make_response(text: str) -> MagicMock:
    content = MagicMock()
    content.text = text
    content.type = "text"
    resp = MagicMock()
    resp.content = [content]
    resp.stop_reason = "end_turn"
    return resp


@pytest.mark.asyncio
async def test_copilot_returns_reply_and_appends_to_history(chat_history):
    agent = CopilotAgent(user_id="u1")

    with patch("app.agents.base.get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=_make_response("Carbon has 6 protons."))
        mock_get.return_value = mock_client

        reply, updated = await agent.chat(chat_history, "How many protons does carbon have?")

    assert reply == "Carbon has 6 protons."
    assert updated[-1] == {"role": "assistant", "content": "Carbon has 6 protons."}
    assert updated[-2]["role"] == "user"


@pytest.mark.asyncio
async def test_copilot_trims_history_when_over_threshold(sample_topic):
    agent = CopilotAgent(user_id="u1")
    long_history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"msg {i}"}
        for i in range(12)
    ]

    summary_resp = _make_response("Summary.")
    chat_resp = _make_response("Answer.")

    with patch("app.agents.copilot_agent.get_client") as mock_trim, \
         patch("app.agents.base.get_client") as mock_base:
        mock_trim_client = AsyncMock()
        mock_trim_client.messages.create = AsyncMock(return_value=summary_resp)
        mock_trim.return_value = mock_trim_client

        mock_base_client = AsyncMock()
        mock_base_client.messages.create = AsyncMock(return_value=chat_resp)
        mock_base.return_value = mock_base_client

        agent = CopilotAgent(user_id="u1")
        reply, updated = await agent.chat(long_history, "Continue")

    assert reply == "Answer."
    assert len(updated) < len(long_history) + 2


@pytest.mark.asyncio
async def test_copilot_does_not_trim_short_history(chat_history):
    agent = CopilotAgent(user_id="u1")

    with patch("app.agents.copilot_agent.get_client") as mock_trim, \
         patch("app.agents.base.get_client") as mock_base:
        mock_base_client = AsyncMock()
        mock_base_client.messages.create = AsyncMock(return_value=_make_response("Answer."))
        mock_base.return_value = mock_base_client

        mock_trim_client = AsyncMock()
        mock_trim.return_value = mock_trim_client

        agent = CopilotAgent(user_id="u1")
        await agent.chat(chat_history, "Question")

    mock_trim_client.messages.create.assert_not_called()


@pytest.mark.asyncio
async def test_copilot_tool_use_loop_resolves():
    """Agent should handle a tool_use response followed by end_turn."""
    agent = CopilotAgent(user_id="u1")

    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.id = "tu_1"
    tool_block.name = "get_available_topics"
    tool_block.input = {}

    tool_resp = MagicMock()
    tool_resp.content = [tool_block]
    tool_resp.stop_reason = "tool_use"

    final_resp = _make_response("You can study Periodic Table next.")

    with patch("app.agents.base.get_client") as mock_get, \
         patch("app.tools.graph_tools.GraphClient") as MockGraph:
        MockGraph.return_value.get_available_topics = AsyncMock(return_value=[
            {"id": "t2", "name": "Periodic Table", "status": "available"}
        ])
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=[tool_resp, final_resp])
        mock_get.return_value = mock_client

        reply, _ = await agent.chat([], "What can I study next?")

    assert "Periodic Table" in reply
