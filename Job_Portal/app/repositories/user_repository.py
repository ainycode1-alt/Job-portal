from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from app.models.user import User
from app.models.client_profile import ClientProfile
from app.models.vendor_profile import VendorProfile


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int | str) -> User | None:
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return None
        result = await self.db.execute(select(User).where(User.id == uid))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def has_profile(self, user_id: int | str) -> bool:
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return False

        # Use exists subquery to optimize performance by avoiding full row load and instantiation
        client_exists = await self.db.execute(select(exists().where(ClientProfile.user_id == uid)))
        if client_exists.scalar():
            return True

        vendor_exists = await self.db.execute(select(exists().where(VendorProfile.user_id == uid)))
        return bool(vendor_exists.scalar())
