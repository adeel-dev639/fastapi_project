from typing import Optional
from pydantic import BaseModel,EmailStr
from datetime import datetime
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class CreatePost(PostBase):
    pass




class CreateUser(BaseModel):
    email: EmailStr 
    password: str

class UserOut(BaseModel):
    id: int 
    email: EmailStr
    class Config:
        orm_mode=True
class Userlogin(BaseModel):
    email: EmailStr
    password:str

class Post(BaseModel):
    id:int
    title: str
    content: str
    published: bool
    created_at:datetime
    owner_id:int
    owner:UserOut
    class Config:
        orm_mode=True
 

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id:Optional[str]=None