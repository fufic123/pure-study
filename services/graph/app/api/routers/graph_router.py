from fastapi import APIRouter

from app.api.handlers.graph_handler import GraphHandler

_h = GraphHandler()

router = APIRouter()

# Courses
router.add_api_route("/courses", _h.create_course, methods=["POST"], status_code=201)
router.add_api_route("/courses", _h.list_courses, methods=["GET"])
router.add_api_route("/courses/{course_id}", _h.get_course, methods=["GET"])

# Topics
router.add_api_route("/topics", _h.list_topics, methods=["GET"])
router.add_api_route("/topics", _h.create_topic, methods=["POST"], status_code=201)
router.add_api_route("/topics/available", _h.get_available_topics, methods=["GET"])
router.add_api_route("/topics/{topic_id}", _h.get_topic, methods=["GET"])
router.add_api_route("/topics/{topic_id}/transition", _h.transition_topic, methods=["PATCH"])
router.add_api_route("/topics/{topic_id}/content-ready", _h.mark_content_ready, methods=["POST"])

# Edges
router.add_api_route("/edges", _h.create_edge, methods=["POST"], status_code=201)
router.add_api_route("/edges", _h.delete_edge, methods=["DELETE"])
