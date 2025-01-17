from sqlmodel import Session, select
from app.models import User, UserCreate
from app.core.security import get_password_hash
from app.core import db_utils
from app import config

def filter_user_by_email(email: str, session: Session):
    # filter the user by email
    query = select(User).where(User.email == email)
    curr_user = session.exec(query).first()
    
    return curr_user

def create_user_in_db(*, session: Session, new_user: UserCreate) -> User:
    user_obj = User.model_validate(
        new_user, update={"hashed_password": get_password_hash(new_user.password)}
    )
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    return user_obj
    