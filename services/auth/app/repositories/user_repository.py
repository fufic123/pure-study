import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.created_at.desc()))
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return int(result.scalar_one() or 0)

    async def create(
        self,
        email: str,
        hashed_password: str | None = None,
        google_id: str | None = None,
        full_name: str | None = None,
        program: str | None = None,
        year_of_study: int | None = None,
        status: UserStatus = UserStatus.ACTIVE,
        is_admin: bool = False,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            google_id=google_id,
            full_name=full_name,
            program=program,
            year_of_study=year_of_study,
            status=status,
            is_admin=is_admin,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_google_id(self, user_id: uuid.UUID, google_id: str) -> User:
        user = await self.get_by_id(user_id)
        user.google_id = google_id  # type: ignore[union-attr]
        await self.session.flush()
        return user  # type: ignore[return-value]

    async def update_profile(
        self,
        user_id: uuid.UUID,
        full_name: str | None = None,
        program: str | None = None,
        year_of_study: int | None = None,
        status: UserStatus | None = None,
        email: str | None = None,
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        if full_name is not None:
            user.full_name = full_name
        if program is not None:
            user.program = program
        if year_of_study is not None:
            user.year_of_study = year_of_study
        if status is not None:
            user.status = status
        if email is not None:
            user.email = email
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: uuid.UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.flush()
        return True
