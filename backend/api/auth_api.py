from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session  

from database.connection import get_db
from services.auth_services import AuthService
from pydantic_schemas.auth_schemas import UserLogin, UserRegister

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register(db_session: Annotated[Session, Depends(get_db)], user: UserRegister):

    return await AuthService(db_session).register_user(user.username, user.password, user.email)


@auth_router.post("/login")
async def login(db_session: Annotated[Session, Depends(get_db)], user: UserLogin):
    return await AuthService(db_session).login_user(user.email, user.password)
