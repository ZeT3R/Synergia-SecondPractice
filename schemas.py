from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TagBase(BaseModel):
    name: str
    class Config: from_attributes = True

class CommentBase(BaseModel):
    text: str
    class Config: from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    is_hidden: bool = False

class PostCreate(PostBase):
    tags: List[str] = []

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    tags: List[TagBase] = []
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
