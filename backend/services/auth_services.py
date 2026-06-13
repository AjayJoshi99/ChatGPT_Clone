from repositories.auth_repo import AuthRepo


class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.user_repository = AuthRepo(self.db_session)

    async def register_user(self, username: str, password: str, email: str):
        user = await self.user_repository.register(username, password, email)
        return user
        
    
    async def login_user(self, username: str, password: str):
        user = await self.user_repository.authenticate_user(username, password)
        if user:
            return {"message": f"User {username} logged in successfully"}
        return {"message": "Invalid credentials"}