from datetime import datetime
from sqlalchemy import select

from db_schemas.db_tables import User


class AuthRepo:
    def __init__(self, db_session):
        self.db_session = db_session

    async def register(self, username: str, password: str, email: str):
        user = User(username=username, password_hash=password, email=email, created_at=datetime.utcnow())
        self.db_session.add(user)
        await self.db_session.commit()
        return user

    async def authenticate_user(self, username: str, password: str):
        query = select(User).where(User.username == username)
        result = await self.db_session.execute(query)
        
        user = result.scalars().first()       
        if user and user.password_hash == password:
            return user
        return None