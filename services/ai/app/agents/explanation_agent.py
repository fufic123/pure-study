from app.agents.base import BaseAgent
from app.models import Model
from app.tools.definitions import GET_TOPIC
from app.tools.graph_tools import make_graph_tools

_SYSTEMS = {
    1: """You are a first-principles teacher. Explain the concept by tracing the causal chain
from fundamentals — why it works at a deep mechanistic level. Be precise but accessible. 3-5 paragraphs.""",

    2: """You are teaching via analogy and intuition. The student didn't understand the first-principles
explanation. Find a vivid real-world analogy that maps cleanly onto the concept without losing its core meaning.
Explain the analogy, then show explicitly how it maps to the concept. 3-4 paragraphs.""",

    3: """You are conducting a Socratic dialogue. The student still doesn't understand.
Do NOT explain directly. Ask leading questions that guide the student to discover the answer themselves.
Start with something they definitely know, build up step by step. Ask one question at a time.""",
}

_MODELS = {
    1: Model.HAIKU,
    2: Model.SONNET,
    3: Model.OPUS,
}


class ExplanationAgent(BaseAgent):
    def __init__(self, user_id: str, level: int) -> None:
        if level not in (1, 2, 3):
            raise ValueError(f"Invalid explanation level {level}")
        self.model = _MODELS[level]
        self.system_prompt = _SYSTEMS[level]
        super().__init__(user_id)

    def _register_tools(self) -> None:
        graph = make_graph_tools(self.user_id)
        self._add_tool(GET_TOPIC, graph["get_topic"])
