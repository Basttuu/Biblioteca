# backend/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    review: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available: bool = True

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=4)

class User(UserBase):
    id: int
    role: Optional[str] = "reader"

    class Config:
        orm_mode = True

class LoanBase(BaseModel):
    book_id: int

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: int
    user_id: int
    borrowed_at: datetime
    returned_at: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[str]
    role: Optional[str]