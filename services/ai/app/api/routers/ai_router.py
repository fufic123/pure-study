from fastapi import APIRouter

from app.api.handlers.ai_handler import AIHandler

_h = AIHandler()

router = APIRouter()

router.add_api_route("/onboarding/message", _h.onboarding_message, methods=["POST"])
router.add_api_route("/explain", _h.explain, methods=["POST"])
router.add_api_route("/copilot/message", _h.copilot_message, methods=["POST"])
router.add_api_route("/graph/next-level", _h.generate_next_level, methods=["POST"])
