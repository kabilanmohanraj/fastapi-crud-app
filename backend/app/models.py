from datetime import date
from enum import Enum
from typing import Union
from sqlmodel import AutoString, SQLModel, Field
from pydantic import EmailStr

# 
# models for user registration and login
class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255, unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    
class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=5, max_length=30)

class UserLogin(UserRegister):
    pass

class UserCreate(UserBase):
    password: str = Field(min_length=5, max_length=30)

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True) # enable auto-increment for id
    hashed_password: str

class UserPublic(SQLModel):
    id: int

# 
# models for books in the library

class Genre(Enum):
    Mystery = "Mystery"
    Fantasy = "Fantasy"
    Fiction = "Fiction"
    Romance = "Romance"
    Adventure = "Adventure"
    Horror = "Horror"
    Science_Fiction = "Science Fiction"
    Classic = "Classic"
    
class BookBase(SQLModel):
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    published_date: date
    summary: Union[str, None] = Field(default=None, max_length=1000)
    genre: Union[Genre, None] = Field(default=None, sa_type=AutoString)

class Books(BookBase, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)

class BookPublic(Books):
    pass

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: Union[str, None] = Field(default=None, min_length=1, max_length=255)
    author: Union[str, None] = Field(default=None, min_length=1, max_length=255)
    published_date: Union[date, None] = None
    summary: Union[str, None] = None
    genre: Union[Genre, None] = None
    
# 
# models for JWT authentication
# the access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

# contents of the JWT token
class TokenData(SQLModel):
    sub: Union[str, None] = None