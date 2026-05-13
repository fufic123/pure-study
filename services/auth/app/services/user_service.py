import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.user_dtos import UserCreateRequest, UserResponse, UserUpdateRequest
from app.repositories.user_repository import UserRepository
from app.services.auth_service import _hash_password

log = logging.getLogger("user_service")


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def list_users(self) -> list[UserResponse]:
        users = await self.users.list_all()
        return [UserResponse.from_orm_user(u) for u in users]

    async def get_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse.from_orm_user(user)

    async def create_user(self, body: UserCreateRequest) -> UserResponse:
        if await self.users.get_by_email(body.email):
            log.warning("create_user duplicate email | email=%s", body.email)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = await self.users.create(
            email=body.email,
            hashed_password=_hash_password(body.password),
            full_name=body.full_name,
            program=body.program,
            year_of_study=body.year_of_study,
            status=body.status,
        )
        await self.session.commit()
        log.info("user created | id=%s email=%s", user.id, user.email)
        return UserResponse.from_orm_user(user)

    async def update_user(self, user_id: uuid.UUID, body: UserUpdateRequest) -> UserResponse:
        existing = await self.users.get_by_id(user_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if body.email and body.email != existing.email:
            clash = await self.users.get_by_email(body.email)
            if clash and clash.id != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

        updated = await self.users.update_profile(
            user_id=user_id,
            email=body.email,
            full_name=body.full_name,
            program=body.program,
            year_of_study=body.year_of_study,
            status=body.status,
        )
        await self.session.commit()
        log.info("user updated | id=%s", user_id)
        return UserResponse.from_orm_user(updated)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        ok = await self.users.delete(user_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.session.commit()
        log.info("user deleted | id=%s", user_id)
