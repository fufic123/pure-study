import logging

from fastapi import Header

from app.agents.copilot_agent import CopilotAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.graph_gen_agent import GraphGenAgent
from app.agents.onboarding_agent import OnboardingAgent
from app.api.dtos.ai_dtos import (
    CopilotRequest,
    CopilotResponse,
    ExplainRequest,
    ExplainResponse,
    NextLevelRequest,
    OnboardingMessageRequest,
    OnboardingMessageResponse,
)
from app.clients.graph_client import GraphClient

log = logging.getLogger("ai_handler")


class AIHandler:
    # ── Onboarding ────────────────────────────────────────────────────────────

    async def onboarding_message(
        self,
        body: OnboardingMessageRequest,
        x_user_id: str = Header(...),
    ) -> OnboardingMessageResponse:
        log.info("onboarding | user=%s history_len=%d msg=%s",
                 x_user_id, len(body.history), body.message[:80])
        agent = OnboardingAgent(user_id=x_user_id)
        messages = body.history + [{"role": "user", "content": body.message}]
        reply = await agent.run(messages)
        course = agent.artifacts.get("course")
        if course:
            log.info("onboarding complete | user=%s course_id=%s", x_user_id, course.get("id"))
        return OnboardingMessageResponse(reply=reply, done=course is not None, course=course)

    # ── Explanation ───────────────────────────────────────────────────────────

    async def explain(
        self,
        body: ExplainRequest,
        x_user_id: str = Header(...),
    ) -> ExplainResponse:
        log.info("explain | user=%s topic=%s level=%d", x_user_id, body.topic_id, body.level)
        agent = ExplanationAgent(user_id=x_user_id, level=body.level)
        messages = (body.history or []) + [
            {"role": "user", "content": f"Explain topic_id={body.topic_id}. {body.message or ''}".strip()}
        ]
        text = await agent.run(messages)
        log.info("explain done | user=%s topic=%s level=%d len=%d",
                 x_user_id, body.topic_id, body.level, len(text))
        return ExplainResponse(text=text)

    # ── Copilot ───────────────────────────────────────────────────────────────

    async def copilot_message(
        self,
        body: CopilotRequest,
        x_user_id: str = Header(...),
    ) -> CopilotResponse:
        log.info("copilot | user=%s topic=%s msg=%s", x_user_id, body.topic_id, body.message[:80])
        agent = CopilotAgent(user_id=x_user_id)
        reply, updated_history = await agent.chat(body.history, body.message)
        log.info("copilot done | user=%s reply_len=%d", x_user_id, len(reply))
        return CopilotResponse(reply=reply, history=updated_history)

    # ── Graph generation ──────────────────────────────────────────────────────

    async def generate_next_level(
        self,
        body: NextLevelRequest,
        x_user_id: str = Header(...),
    ) -> dict:
        log.info("graph_gen | user=%s course=%s mastered_topic=%s subject=%s",
                 x_user_id, body.course_id, body.mastered_topic_id, body.subject)
        graph = GraphClient(x_user_id)
        mastered_topic = await graph.get_topic(body.mastered_topic_id)

        agent = GraphGenAgent(user_id=x_user_id)
        await agent.run([{
            "role": "user",
            "content": (
                f"Generate the next wave of topics for course_id={body.course_id}.\n"
                f"The user just mastered: {mastered_topic['name']} (id={mastered_topic['id']}, slug={mastered_topic['slug']}).\n"
                f"Subject: {body.subject}."
            ),
        }])
        log.info("graph_gen done | user=%s", x_user_id)
        return {"ok": True}
