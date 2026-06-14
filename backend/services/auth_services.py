from fastapi import HTTPException

from repositories.auth_repo import AuthRepo
from core.security import create_access_token, create_refresh_token


class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.user_repository = AuthRepo(self.db_session)

    async def register_user(self, username: str, password: str, email: str):

        if await self.user_repository.check_user_exists(username, email):
            raise HTTPException(detail="Username or email already exists", status_code=403)

        user = await self.user_repository.register(username, password, email)
        return user

    async def login_user(self, username: str, password: str):
        user = await self.user_repository.authenticate_user(username, password)

        print(user)
        access_token = create_access_token(
            {"username": user.username, "user_id": user.id}
        )
        refresh_token = create_refresh_token(
            {"username": user.username, "user_id": user.id}
        )

        if user:
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        
        return {"message": "Invalid credentials"}
