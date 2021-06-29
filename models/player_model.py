from pydantic import BaseModel, Field
from typing import List
from models.misc_models import PyObjectId
from bson import ObjectId


class PlayerBase(BaseModel):
    mc_username: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    mc_username: str = None
    mc_uuid: str = None
    badges: List[str] = None


class Player(PlayerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    mc_username: str
    mc_uuid: str
    badges: List[str] = []
    
