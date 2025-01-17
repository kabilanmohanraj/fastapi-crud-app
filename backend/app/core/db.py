from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select
from backend.app import config
from backend.app.models import User, UserCreate
from backend.app.core import db_utils

connect_args = {"check_same_thread": False}
engine = create_engine(str(config.SQLITE_DB_URL), connect_args=connect_args)

def get_db():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]

def init_db():
    # create the database tables
    SQLModel.metadata.create_all(engine)
    
    # create first admin user, if not exists
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == config.FIRST_ADMIN_USER_EMAIL)
        ).first()
        if not user:
            user_in = UserCreate(
                email=config.FIRST_ADMIN_USER_EMAIL,
                password=config.FIRST_ADMIN_USER_PASSWORD,
                is_superuser=True,
            )
            user = db_utils.create_user_in_db(session=session, new_user=user_in)
            print("Admin user created successfully")