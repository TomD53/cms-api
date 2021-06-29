from pydantic import BaseModel, Field
from typing import List
from models.misc_models import PyObjectId
from bson import ObjectId


class TeamBase(BaseModel):
    name: str
    alias: str
    description: str = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    name: str = None
    alias: str = None
    description: str = None
    logo_url: str = None
    is_active: bool = True


class Team(TeamBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    logo_url: str = None
    is_active: bool = True
    managers: List[str] = []  # User IDs
    players: List[str] = []  # Player IDs
    badges: List[str] = []  # Badge IDs