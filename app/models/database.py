from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    username: str
    password: str
    active: bool
    role: str | None = None

class Book(BaseModel):
    id: Optional[int] = None
    name: str 
    author: str
    editorial: str

class Loan(BaseModel):
    user_id: Optional[int] = None
    book_id: int
