from fastapi import APIRouter, Depends, Response
from typing import Annotated
from sqlalchemy.orm import Session  
from fastapi.security import OAuth2PasswordRequestForm

from database.connection import get_db
from services.auth_services import AuthService
from pydantic_schemas.auth_schemas import UserLogin, UserRegister

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register(db_session: Annotated[Session, Depends(get_db)], user: UserRegister):

    return await AuthService(db_session).register_user(user.username, user.password, user.email)


@auth_router.post("/login")
async def login(db_session: Annotated[Session, Depends(get_db)], user: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response,):
    result =  await AuthService(db_session).login_user(user.username, user.password)
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,       
        secure=True,         
        samesite="lax",      
        max_age=1440 * 60,   
        path="/auth"
    )
    return result
    
