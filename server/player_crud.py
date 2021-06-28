from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, Response
from typing import Optional, List
from fastapi.encoders import jsonable_encoder
from mojang import MojangAPI

from app import db

from models import player_model, misc_models

router = APIRouter(
    prefix="/players"
)


@router.get("/", response_description="List all players", response_model=List[player_model.Player])
async def get_players():
    # passing None for no limit to the amount of players returned
    players = await db["players"].find().to_list(None)
    return players


@router.post(
    "/",
    response_description="Add new player",
    response_model=player_model.Player,
    responses={
        # defining other possible responses
        400: {
            "model": misc_models.Message, 
            "description": "Raised when the username already exists"
        },
        404: {
            "model": misc_models.Message, 
            "description": "Raised when a minecraft UUID cannot be found for the provided username"
        }
    }
)
async def add_player(player: player_model.PlayerCreate):
    existing_player = await db["players"].find_one({"mc_username": player.mc_username})
    if existing_player:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Player {player.mc_username} already exists"}
        )
    uuid = MojangAPI.get_uuid(player.mc_username)
    if not uuid:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"Minecraft UUID for player {player.mc_username} does not exist"}
        )
    player_with_uuid = player_model.Player(
        mc_uuid=uuid,
        mc_username=player.mc_username
    )
    new_player = await db["players"].insert_one(jsonable_encoder(player_with_uuid))
    created_player = await db["players"].find_one({"_id": new_player.inserted_id})
    return created_player


@router.get(
    "/id/{player_id}",
    response_description="Get a player by their ID",
    response_model=player_model.Player,
    responses={
        404: {"model": misc_models.Message}
    }
)
async def get_player_by_id(player_id: str):
    player = await db["players"].find_one({"_id": player_id})
    if player:
        return player
    else:
        return JSONResponse(status_code=404, content={"message": f"Could not find player with ID {player_id}"})


@router.get(
    "/mc_username/{mc_username}",
    response_description="Get a player by their minecraft username",
    response_model=player_model.Player,
    responses={
        404: {"model": misc_models.Message}
    }
)
async def get_player_by_username(mc_username: str):
    player = await db["players"].find_one({"mc_username": mc_username})
    if player:
        return player
    else:
        return JSONResponse(status_code=404, content={"message": f"Could not find player with username {mc_username}"})


@router.delete(
    "/{player_id}",
    response_description="Delete a player by their ID",
    response_model=player_model.Player
)
async def delete_player(player_id: str):
    delete_result = await db["players"].delete_one({"_id": player_id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return JSONResponse(status_code=404, content={"message": f"Could not find player with ID {player_id}"})
