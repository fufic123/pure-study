from fastapi import APIRouter

from app.api.handlers.user_handler import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
    users_report_html,
    users_report_xml,
    users_report_xsl,
)

router = APIRouter()

# Report routes must come BEFORE /{user_id} so "report" isn't parsed as a UUID
router.get("/users/report.xml", summary="Export users as XML")(users_report_xml)
router.get("/users/report.xsl", summary="XSLT stylesheet")(users_report_xsl)
router.get("/users/report.html", summary="XSLT-rendered HTML report")(users_report_html)

router.get("/users", summary="List all users")(list_users)
router.post("/users", status_code=201, summary="Create a user")(create_user)
router.get("/users/{user_id}", summary="Get a user")(get_user)
router.patch("/users/{user_id}", summary="Update a user")(update_user)
router.delete("/users/{user_id}", summary="Delete a user")(delete_user)
