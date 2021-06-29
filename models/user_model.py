from pydantic import BaseModel, Field, EmailStr
from typing import List
from models.misc_models import PyObjectId
from bson import ObjectId


class UserBase(BaseModel):
    username: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_admin: bool = False
    player: str = None


class UserInDB(User):
    hashed_password: str
