from fastapi.security import OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

import app.config as config
from app.models import Token, TokenData, UserLogin
from app.core.db import SessionDep
from app.core.db_utils import filter_user_by_email
from app.models import User
from app.core.security import verify_password, TokenDep


from typing import Annotated, Union

router = APIRouter(tags=["login"])

def authenticate_user(user: UserLogin, session: SessionDep):
    # check if the user exists in the database
    user_in_db = filter_user_by_email(user.email, session)
    if not user_in_db:
        return None
    
    # if the user exists, check if the password is correct
    if not verify_password(user.password, user_in_db.hashed_password):
        return None
    
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    
    return encoded_jwt

async def get_current_user(session: SessionDep, token: TokenDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
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

@router.post(
    "/login",
    summary="User Login",
    description=(
        "Authenticate a user by validating their email and password. "
        "Returns a JSON Web Token (JWT) if the credentials are correct."
    ),
    response_model=Token,
    responses={
        200: {
            "description": "Successful login with a JWT token.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "aksbfkasjhfkahDsSDasdDSD...",
                        "token_type": "bearer"
                    }
                }
            },
        },
        404: {"description": "Incorrect username or password."},
    },
)
async def user_login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    # check if the user has already registered
    user = authenticate_user(UserLogin(email=form_data.username, password=form_data.password), session)
    if not user:
        # if not, raise an HTTP 404 exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect username or password")

    # if the user is found, return a newly generated JWT token
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")
