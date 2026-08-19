from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(pattern=r"[a-zA-Z0-9_]{3,20}$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str

class PostCreate(BaseModel):
    user_id: int # TEMPORARY UNTIL AUTHENTICATION
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)

class PostResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
