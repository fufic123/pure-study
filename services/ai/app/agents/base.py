import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable

from app.clients.anthropic_client import get_client

log = logging.getLogger("agent")


class BaseAgent(ABC):
    """
    Tool-use agent loop over Anthropic messages API.

    Subclasses define:
      model          — which Claude model to use
      system_prompt  — agent's persona and task description
      _register_tools() — wires tool schemas + async handlers
    """

    model: str
    system_prompt: str

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.artifacts: dict[str, Any] = {}
        self._tool_schemas: list[dict] = []
        self._tool_handlers: dict[str, Callable] = {}
        self._register_tools()

    @abstractmethod
    def _register_tools(self) -> None:
        """Called once at init. Populate _tool_schemas and _tool_handlers."""

    def _add_tool(self, schema: dict, handler: Callable) -> None:
        self._tool_schemas.append(schema)
        self._tool_handlers[schema["name"]] = handler

    async def run(self, messages: list[dict], max_iterations: int = 10) -> str:
        agent_name = type(self).__name__
        t0 = time.monotonic()
        log.info(
            "[%s] start | user=%s model=%s tools=%s msgs=%d",
            agent_name, self.user_id, self.model,
            [s["name"] for s in self._tool_schemas],
            len(messages),
        )

        client = get_client()
        current = list(messages)

        for iteration in range(max_iterations):
            kwargs: dict[str, Any] = dict(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=current,
            )
            if self._tool_schemas:
                kwargs["tools"] = self._tool_schemas

            log.debug("[%s] iter=%d calling Anthropic | msgs=%d", agent_name, iteration, len(current))
            iter_t0 = time.monotonic()
            response = await client.messages.create(**kwargs)
            iter_ms = int((time.monotonic() - iter_t0) * 1000)

            log.debug(
                "[%s] iter=%d response | stop_reason=%s blocks=%d %dms",
                agent_name, iteration, response.stop_reason, len(response.content), iter_ms,
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        total_ms = int((time.monotonic() - t0) * 1000)
                        log.info(
                            "[%s] done | iters=%d total=%dms reply_len=%d",
                            agent_name, iteration + 1, total_ms, len(block.text),
                        )
                        return block.text
                return ""

            if response.stop_reason == "tool_use":
                tool_results = await self._dispatch(response.content, agent_name)
                current = current + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results},
                ]
                continue

            log.warning("[%s] unexpected stop_reason=%s — aborting", agent_name, response.stop_reason)
            break

        total_ms = int((time.monotonic() - t0) * 1000)
        log.warning("[%s] exhausted max_iterations=%d | total=%dms", agent_name, max_iterations, total_ms)
        return ""

    async def _dispatch(self, content: list, agent_name: str = "") -> list[dict]:
        results = []
        for block in content:
            if block.type != "tool_use":
                continue

            input_preview = json.dumps(block.input, ensure_ascii=False)[:200]
            log.info(
                "[%s] tool_call | %s(%s)",
                agent_name or type(self).__name__, block.name, input_preview,
            )

            handler = self._tool_handlers.get(block.name)
            if not handler:
                log.warning("[%s] unknown tool=%s", agent_name, block.name)
                payload = json.dumps({"error": f"unknown tool '{block.name}'"})
                is_error = True
            else:
                t0 = time.monotonic()
                try:
                    result = await handler(block.input)
                    payload = json.dumps(result, ensure_ascii=False, default=str)
                    is_error = False
                    ms = int((time.monotonic() - t0) * 1000)
                    log.debug(
                        "[%s] tool_result | %s → %dms | %s",
                        agent_name, block.name, ms, payload[:200],
                    )
                except Exception as exc:
                    payload = str(exc)
                    is_error = True
                    ms = int((time.monotonic() - t0) * 1000)
                    log.error(
                        "[%s] tool_error | %s → %dms | %s",
                        agent_name, block.name, ms, exc,
                    )

            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": payload,
                "is_error": is_error,
            })
        return results
