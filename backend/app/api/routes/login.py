from fastapi.security import OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException

import backend.app.config as config
from backend.app.models import Token, UserLogin
from backend.app.core.db import SessionDep
from backend.app.core.db_utils import filter_user_by_email
from backend.app.core.security import verify_password


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

@router.post(
    "/login",
    summary="User Login",
    description=(
        "Authenticate a user by validating their email and password. "
        "Returns a JSON Web Token (JWT) if the credentials are correct."
        "The endpoint uses FastAPI's OAuth2PasswordRequestForm class to parse the form data, where `username` and `password` are required fields. Other fields are optional."
        "In our endpoint, `username` is the user's email and `password` is the user's password."
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
        raise HTTPException(status_code=404, detail="Incorrect username or password")

    # if the user is found, return a newly generated JWT token
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")
