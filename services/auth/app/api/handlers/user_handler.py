import uuid
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from fastapi import Depends, Header, HTTPException, Path as PathParam, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.user_dtos import UserCreateRequest, UserResponse, UserUpdateRequest
from app.db.session import get_session
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


async def require_admin(
    x_user_id: str = Header(...),
    session: AsyncSession = Depends(get_session),
) -> uuid.UUID:
    """Reject the request if the caller (set by the gateway via x-user-id) isn't an admin."""
    try:
        uid = uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid caller id")
    user = await UserRepository(session).get_by_id(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Caller not found")
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return uid

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


async def list_users(
    session: AsyncSession = Depends(get_session),
    _admin: uuid.UUID = Depends(require_admin),
) -> list[UserResponse]:
    return await UserService(session).list_users()


async def get_user(
    user_id: uuid.UUID = PathParam(...),
    session: AsyncSession = Depends(get_session),
    _admin: uuid.UUID = Depends(require_admin),
) -> UserResponse:
    return await UserService(session).get_user(user_id)


async def create_user(
    body: UserCreateRequest,
    session: AsyncSession = Depends(get_session),
    _admin: uuid.UUID = Depends(require_admin),
) -> UserResponse:
    return await UserService(session).create_user(body)


async def update_user(
    body: UserUpdateRequest,
    user_id: uuid.UUID = PathParam(...),
    session: AsyncSession = Depends(get_session),
    _admin: uuid.UUID = Depends(require_admin),
) -> UserResponse:
    return await UserService(session).update_user(user_id, body)


async def delete_user(
    user_id: uuid.UUID = PathParam(...),
    session: AsyncSession = Depends(get_session),
    _admin: uuid.UUID = Depends(require_admin),
) -> dict:
    await UserService(session).delete_user(user_id)
    return {"detail": "deleted"}


def _users_to_xml(users: list[UserResponse]) -> str:
    rows = []
    for u in users:
        rows.append(
            "  <user>\n"
            f"    <id>{xml_escape(str(u.id))}</id>\n"
            f"    <email>{xml_escape(u.email)}</email>\n"
            f"    <full_name>{xml_escape(u.full_name or '')}</full_name>\n"
            f"    <program>{xml_escape(u.program or '')}</program>\n"
            f"    <year_of_study>{u.year_of_study or ''}</year_of_study>\n"
            f"    <status>{xml_escape(u.status.value)}</status>\n"
            f"    <created_at>{u.created_at.isoformat()}</created_at>\n"
            "  </user>"
        )
    body = "\n".join(rows) if rows else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<?xml-stylesheet type="text/xsl" href="/auth/users/report.xsl"?>\n'
        "<users>\n"
        f"{body}\n"
        "</users>\n"
    )


async def users_report_xml(
    session: AsyncSession = Depends(get_session),
    _admin: uuid.UUID = Depends(require_admin),
) -> Response:
    users = await UserService(session).list_users()
    xml = _users_to_xml(users)
    return Response(content=xml, media_type="application/xml")


async def users_report_xsl() -> Response:
    xsl_path = _TEMPLATES_DIR / "users_report.xsl"
    if not xsl_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="XSLT stylesheet missing",
        )
    return Response(content=xsl_path.read_text(encoding="utf-8"), media_type="application/xslt+xml")


async def users_report_html(
    session: AsyncSession = Depends(get_session),
    _admin: uuid.UUID = Depends(require_admin),
) -> Response:
    """Server-side XSLT transform — returns ready-to-render HTML."""
    try:
        from lxml import etree
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="lxml not installed",
        )

    users = await UserService(session).list_users()
    xml_str = _users_to_xml(users)
    xsl_path = _TEMPLATES_DIR / "users_report.xsl"
    if not xsl_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="XSLT stylesheet missing",
        )

    xml_doc = etree.fromstring(xml_str.encode("utf-8"))
    xsl_doc = etree.parse(str(xsl_path))
    transform = etree.XSLT(xsl_doc)
    html_doc = transform(xml_doc)
    return Response(content=str(html_doc), media_type="text/html; charset=utf-8")
