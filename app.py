from fastapi import FastAPI
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.cms_api

import server.player_crud
import server.team_crud
import server.oauth2

app.include_router(server.player_crud.router)
app.include_router(server.team_crud.router)
app.include_router(server.oauth2.router)