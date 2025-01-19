from typing import Annotated

from fastapi import Depends, HTTPException
import jwt

from backend.app import config
from backend.app.core.db import SessionDep
from backend.app.core.security import TokenDep
from backend.app.core.db_utils import filter_user_by_email
from backend.app.models import TokenData, User

async def get_current_user(session: SessionDep, token: TokenDep):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(sub=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = filter_user_by_email(token_data.sub, session)
    
    # check if user exists
    if user is None:
        raise credentials_exception
    
    # check if user is active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]