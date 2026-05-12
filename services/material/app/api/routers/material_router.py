from fastapi import APIRouter

from app.api.handlers.material_handler import MaterialHandler

_h = MaterialHandler()

router = APIRouter()

router.add_api_route("/sources", _h.list_sources, methods=["GET"])
router.add_api_route("/search", _h.search, methods=["POST"])
router.add_api_route("/sources/{source_id}/courses/{course_id}/topics", _h.fetch_topics, methods=["GET"])
