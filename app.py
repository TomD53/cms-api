from fastapi import FastAPI
import motor.motor_asyncio
import yaml

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

with open('tags.yaml') as f:
    tags = yaml.load(f, Loader=yaml.FullLoader)

app = FastAPI(
    title="CMS API",
    description="Web service connecting all CMS related apps",
    version="0.1.0",
    openapi_tags=tags["tags"]
)
client = motor.motor_asyncio.AsyncIOMotorClient(config["db_url"])
db = client.cms_api

import server.player_crud
import server.team_crud
import server.oauth2

app.include_router(server.player_crud.router)
app.include_router(server.team_crud.router)
app.include_router(server.oauth2.router)