import logging

from settings import settings

from app.agents.base import BaseAgent
from app.clients.anthropic_client import get_client
from app.models import Model
from app.tools.definitions import GET_AVAILABLE_TOPICS, GET_TOPIC
from app.tools.graph_tools import make_graph_tools

log = logging.getLogger("copilot")

_SYSTEM = """You are a study copilot for a personalised learning platform.
You know which topic the user is studying and can look up their graph state using tools.

Answer questions concisely and clearly. If the user seems confused, suggest escalating
the explanation level. Never give away quiz answers — guide instead.

Use get_topic to refresh topic state when needed. Use get_available_topics to see
what the user can study next and suggest a logical path."""


async def _trim_history(history: list[dict]) -> list[dict]:
    """Summarise older messages with Haiku, keep last N verbatim."""
    keep = settings.copilot_history_keep_last
    old = history[:-keep]
    recent = history[-keep:]

    log.info("trimming history | total=%d old=%d keep=%d", len(history), len(old), keep)
    conversation = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in old)
    client = get_client()
    resp = await client.messages.create(
        model=Model.HAIKU,
        max_tokens=256,
        messages=[{"role": "user", "content": f"Summarise this study conversation in 3-4 sentences:\n\n{conversation}"}],
    )
    summary = resp.content[0].text
    log.debug("history summary: %s", summary[:120])
    return [{"role": "assistant", "content": f"[Conversation summary]: {summary}"}] + recent


class CopilotAgent(BaseAgent):
    model = Model.HAIKU
    system_prompt = _SYSTEM

    def _register_tools(self) -> None:
        graph = make_graph_tools(self.user_id)
        self._add_tool(GET_TOPIC, graph["get_topic"])
        self._add_tool(GET_AVAILABLE_TOPICS, graph["get_available_topics"])

    async def chat(self, history: list[dict], user_message: str) -> tuple[str, list[dict]]:
        log.info("chat | user=%s history_len=%d msg=%s", self.user_id, len(history), user_message[:80])

        if len(history) >= settings.copilot_history_trim_after:
            log.info("history over threshold (%d), trimming", settings.copilot_history_trim_after)
            history = await _trim_history(history)

        messages = history + [{"role": "user", "content": user_message}]
        reply = await self.run(messages)
        log.info("chat done | user=%s reply_len=%d", self.user_id, len(reply))
        return reply, messages + [{"role": "assistant", "content": reply}]
