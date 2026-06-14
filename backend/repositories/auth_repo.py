from datetime import datetime
from sqlalchemy import select, or_
from fastapi import HTTPException

from db_schemas.db_tables import User
from core.security import get_hashed_password, verify_password


class AuthRepo:
    def __init__(self, db_session):
        self.db_session = db_session

    async def check_user_exists(self, username: str, email: str):
        query = select(User).where(or_(User.username == username, User.email == email))
        result = await self.db_session.execute(query)
        return result.scalars().first() is not None

    async def register(self, username: str, password: str, email: str):
        user = User(username=username, password_hash=get_hashed_password(password), email=email, created_at=datetime.utcnow())
        self.db_session.add(user)
        await self.db_session.commit()
        return user

    async def authenticate_user(self, username: str, password: str):
        query = select(User).where(or_(User.username == username))
        result = await self.db_session.execute(query)
        user = result.scalars().first()     
        print(user)
        if user and verify_password(password, user.password_hash) :
            return user
        raise HTTPException(detail="invalid username or password", status_code=401)