from app.agents.base import BaseAgent
from app.models import Model
from app.tools.definitions import (
    CREATE_EDGE,
    CREATE_TOPIC,
    FETCH_COURSE_TOPICS,
    SEARCH_MATERIALS,
)
from app.tools.graph_tools import make_graph_tools
from app.tools.material_tools import make_material_tools

_SYSTEM = """You are a curriculum designer. Given a subject, goal, user level, and a course_id to attach topics to,
generate the next wave of topics for the knowledge graph.

Use search_materials and fetch_course_topics if you need reference material.
Then create topics with create_topic and wire them with create_edge.

Rules:
- complexity 1-10 (match to user level)
- status="locked" for all new topics unless they have no prerequisites in this batch
- Always create CONTAINS (course→topic) and REQUIRES (topic→prerequisite) edges
- Generate 2-5 focused topics per wave, not a full curriculum at once"""


class GraphGenAgent(BaseAgent):
    model = Model.HAIKU
    system_prompt = _SYSTEM

    def _register_tools(self) -> None:
        graph = make_graph_tools(self.user_id)
        material = make_material_tools()

        self._add_tool(SEARCH_MATERIALS, material["search_materials"])
        self._add_tool(FETCH_COURSE_TOPICS, material["fetch_course_topics"])
        self._add_tool(CREATE_TOPIC, graph["create_topic"])
        self._add_tool(CREATE_EDGE, graph["create_edge"])
