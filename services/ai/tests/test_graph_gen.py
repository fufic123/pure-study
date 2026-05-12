from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.graph_gen_agent import GraphGenAgent


def _make_response(text: str) -> MagicMock:
    content = MagicMock()
    content.text = text
    content.type = "text"
    resp = MagicMock()
    resp.content = [content]
    resp.stop_reason = "end_turn"
    return resp


def _tool_response(name: str, tool_id: str, inp: dict) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = name
    block.input = inp
    resp = MagicMock()
    resp.content = [block]
    resp.stop_reason = "tool_use"
    return resp


@pytest.mark.asyncio
async def test_graph_gen_calls_create_topic_and_edge():
    agent = GraphGenAgent(user_id="u1")

    topic_tool = _tool_response("create_topic", "tu_1", {
        "name": "Atomic Structure", "slug": "atomic-structure",
        "domain": "chemistry", "description": "Atoms.", "complexity": 3, "status": "available",
    })
    edge_tool = _tool_response("create_edge", "tu_2", {
        "from_id": "course-1", "to_id": "topic-1", "edge_type": "CONTAINS",
    })
    final = _make_response("Done.")

    with patch("app.agents.base.get_client") as mock_get, \
         patch("app.tools.graph_tools.GraphClient") as MockGraph:
        MockGraph.return_value.create_topic = AsyncMock(return_value={"id": "topic-1", "name": "Atomic Structure"})
        MockGraph.return_value.create_edge = AsyncMock()

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=[topic_tool, edge_tool, final])
        mock_get.return_value = mock_client

        agent = GraphGenAgent(user_id="u1")
        await agent.run([{"role": "user", "content": "Generate next topics for course_id=course-1"}])

    MockGraph.return_value.create_topic.assert_called_once()
    MockGraph.return_value.create_edge.assert_called_once()


@pytest.mark.asyncio
async def test_graph_gen_tool_error_does_not_crash_loop():
    """A failing tool should return is_error=True and let the agent continue."""
    agent = GraphGenAgent(user_id="u1")

    bad_tool = _tool_response("create_topic", "tu_err", {"name": "X"})  # missing required fields
    final = _make_response("Handled the error.")

    with patch("app.agents.base.get_client") as mock_get, \
         patch("app.tools.graph_tools.GraphClient") as MockGraph:
        MockGraph.return_value.create_topic = AsyncMock(side_effect=Exception("validation error"))

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=[bad_tool, final])
        mock_get.return_value = mock_client

        agent = GraphGenAgent(user_id="u1")
        reply = await agent.run([{"role": "user", "content": "Generate"}])

    assert reply == "Handled the error."
    # Tool result with is_error=True was sent back
    second_call_messages = mock_client.messages.create.call_args_list[1].kwargs["messages"]
    tool_result_msg = second_call_messages[-1]
    assert tool_result_msg["role"] == "user"
    assert any(r.get("is_error") for r in tool_result_msg["content"])
