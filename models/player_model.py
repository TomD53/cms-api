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


class Player(PlayerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    mc_uuid: str
    teams: List[int] = []
    badges: List[int] = []
    
