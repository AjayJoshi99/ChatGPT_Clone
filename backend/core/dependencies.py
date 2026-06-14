from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt 
from typing import Annotated
from fastapi import Depends

from core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(access_token : Annotated[str, Depends(oauth2_scheme)]):
    result = decode_access_token(access_token)
    print("result is :", result)
    return result