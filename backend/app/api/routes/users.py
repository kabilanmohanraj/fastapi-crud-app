from typing import Any
from fastapi import APIRouter, HTTPException

from app.core.db import SessionDep
from app.core import db_utils
from app.models import UserCreate, UserPublic, UserRegister

router = APIRouter(prefix="/users", tags=["users"])

# TODO: user signup endpoint
@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = db_utils.filter_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User has already registered",
        )
    
    user_create = UserCreate.model_validate(user_in)
    user = db_utils.create_user_in_db(session=session, user_create=user_create)
    
    return user