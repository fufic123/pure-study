import logging

from settings import settings

from app.agents.base import BaseAgent
from app.clients.anthropic_client import get_client
from app.models import Model
from app.tools.definitions import GET_AVAILABLE_TOPICS, GET_TOPIC
from app.tools.graph_tools import make_graph_tools

log = logging.getLogger("copilot")

_SYSTEM = """You are a study copilot for a personalised learning platform.

You will be told which topic the user is currently studying, which topics they have
already mastered, and which topics are still in progress. Use this context to tailor
every response:

- "give me an example", "show me an example", "explain this" → use the CURRENT topic
  (the one the user is actively studying right now).
- "quiz me", "test me", "questions" → quiz on topics from the MASTERED list (not the
  current one — the user is still learning it). Mix easy and harder questions; cover
  several mastered topics if possible. If there are no mastered topics yet, say so and
  offer to quiz the current topic instead.
- "what's next", "where do I go" → suggest from in_progress or available topics.

Other rules:
- Be concise and clear. Markdown is allowed.
- Never give away quiz answers — guide instead.
- If you need fresh data (e.g. a topic the user names that isn't in the injected
  context), use get_topic / get_available_topics."""


def build_context_block(
    current_topic: dict | None,
    mastered: list[dict],
    in_progress: list[dict],
) -> str:
    def _fmt(topics: list[dict]) -> str:
        if not topics:
            return "  (none)"
        return "\n".join(f"  - {t['name']} (id={t['id']})" for t in topics)

    cur = (
        f"{current_topic['name']} (id={current_topic['id']}, status={current_topic.get('status', '?')})"
        if current_topic else "(none)"
    )
    return (
        "\n\n--- USER GRAPH CONTEXT (injected at request time) ---\n"
        f"Current topic the user is studying:\n  {cur}\n\n"
        f"Mastered topics ({len(mastered)}):\n{_fmt(mastered)}\n\n"
        f"In-progress topics ({len(in_progress)}):\n{_fmt(in_progress)}\n"
        "--- END CONTEXT ---"
    )


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
