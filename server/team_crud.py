from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, Response
from typing import Optional, List
from fastapi.encoders import jsonable_encoder

from app import db

from models import team_model, misc_models, player_model

router = APIRouter(
    prefix="/teams",
    tags=["teams"]
)

@router.get("/", response_description="List all teams", response_model=List[team_model.Team])
async def get_teams():
    # passing None for no limit to the amount of players returned
    teams = await db["teams"].find().to_list(None)
    return teams

@router.post(
    "/",
    response_description="Add new team",
    response_model=team_model.Team,
    responses={
        # defining other possible responses
        400: {
            "model": misc_models.Message,
            "description": "Raised when the team name or alias already exists"
        }
    }
)
async def add_team(team: team_model.TeamCreate):
    existing_team = await db["teams"].find_one({"$or": [
        {"name": team.name},
        {"alias": team.alias}
    ]})
    if existing_team:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Team {existing_team['name']} with alias {existing_team['alias']} already exists"}
        )
    team_obj = team_model.Team(**team.dict())
    new_team = await db["teams"].insert_one(jsonable_encoder(team_obj))
    created_team = await db["teams"].find_one({"_id": new_team.inserted_id})
    return created_team


@router.get(
    "/id/{team_id}",
    response_description="Get a team by its ID",
    response_model=team_model.Team,
    responses={
        404: {
            "model": misc_models.Message,
            "description": "Raised when the specified team cannot be found"
        }
    }
)
async def get_team_by_id(team_id: str):
    team = await db["teams"].find_one({"_id": team_id})
    if team:
        return team
    else:
        return JSONResponse(status_code=404, content={"message": f"Could not find team with ID {team_id}"})


@router.get(
    "/alias/{team_alias}",
    response_description="Get a team by its alias",
    response_model=team_model.Team,
    responses={
        404: {
            "model": misc_models.Message,
            "description": "Raised when the specified team cannot be found"
        }
    }
)
async def get_team_by_alias(team_alias: str):
    team = await db["teams"].find_one({"alias": team_alias})
    if team:
        return team
    else:
        return JSONResponse(status_code=404, content={"message": f"Could not find team with alias {team_alias}"})


@router.delete(
    "/{team_id}",
    response_description="Delete a team by its ID",
    responses={
        404: {
            "model": misc_models.Message,
            "description": "Raised when the specified team cannot be found"
        }
    }
)
async def delete_team(team_id: str):
    delete_result = await db["teams"].delete_one({"_id": team_id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return JSONResponse(status_code=404, content={"message": f"Could not find team with ID {team_id}"})


@router.put(
    "/{team_id}",
    response_description="Update a team",
    response_model=team_model.Team
)
async def update_team(team_id: str, team: team_model.TeamUpdate):
    team = {k: v for k, v in team.dict().items() if v is not None}

    if len(team) >= 1:
        update_result = await db["teams"].update_one({"_id": team_id}, {"$set": team})

        if update_result.modified_count == 1:
            updated_team = await db["teams"].find_one({"_id": team_id})
            if updated_team is not None:
                return updated_team

    existing_team = await db["teams"].find_one({"_id": team_id})
    if existing_team is not None:
        return existing_team


@router.get(
    "/{team_id}/players",
    response_description="Get a team's players",
    response_model=List[player_model.Player],
    responses={
        404: {
            "model": misc_models.Message,
            "description": "Raised when the specified team cannot be found"
        }
    }
)
async def get_team_roster(team_id: str):
    team = await db["teams"].find_one({"_id": team_id})
    if not team:
        return JSONResponse(status_code=404, content={"message": f"Could not find team with ID {team_id}"})

    players = await db["players"].find({"_id": {"$in": team['players']}}).to_list(None)
    return players