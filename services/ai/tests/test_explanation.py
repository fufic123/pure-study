from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.explanation_agent import _MODELS, ExplanationAgent
from app.models import Model


def _make_response(text: str) -> MagicMock:
    content = MagicMock()
    content.text = text
    content.type = "text"
    resp = MagicMock()
    resp.content = [content]
    resp.stop_reason = "end_turn"
    return resp


@pytest.mark.asyncio
async def test_explain_level_1_uses_haiku():
    agent = ExplanationAgent(user_id="u1", level=1)
    assert agent.model == Model.HAIKU

    with patch("app.agents.base.get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=_make_response("Atoms are..."))
        mock_get.return_value = mock_client

        text = await agent.run([{"role": "user", "content": "Explain atomic structure"}])

    call_kwargs = mock_client.messages.create.call_args
    assert call_kwargs.kwargs["model"] == Model.HAIKU
    assert text == "Atoms are..."


@pytest.mark.asyncio
async def test_explain_level_2_uses_sonnet():
    agent = ExplanationAgent(user_id="u1", level=2)
    assert agent.model == Model.SONNET


@pytest.mark.asyncio
async def test_explain_level_3_uses_opus():
    agent = ExplanationAgent(user_id="u1", level=3)
    assert agent.model == Model.OPUS


def test_explain_invalid_level_raises():
    with pytest.raises(ValueError, match="Invalid explanation level"):
        ExplanationAgent(user_id="u1", level=4)


@pytest.mark.asyncio
async def test_explain_level_3_passes_history():
    agent = ExplanationAgent(user_id="u1", level=3)
    history = [
        {"role": "user", "content": "I don't get it"},
        {"role": "assistant", "content": "Have you seen sand?"},
    ]

    with patch("app.agents.base.get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=_make_response("Good!"))
        mock_get.return_value = mock_client

        await agent.run(history + [{"role": "user", "content": "Yes"}])

    messages = mock_client.messages.create.call_args.kwargs["messages"]
    assert any(m["content"] == "Yes" for m in messages)
    assert any(m["content"] == "Have you seen sand?" for m in messages)
