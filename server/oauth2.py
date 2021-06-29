from models import misc_models, user_model
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app import app, db, config



SECRET_KEY = config["secret_key"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/oauth2",
    tags=["oauth2"]
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth2/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str):
    existing_user = await db["users"].find_one({"username": username})
    if existing_user:
        return user_model.UserInDB(**existing_user)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = misc_models.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=misc_models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=user_model.User)
async def read_users_me(current_user: user_model.User = Depends(get_current_user)):
    return current_user.dict()


@router.post(
    "/users/",
    response_model=user_model.User,
    responses={
        400: {
            "model": misc_models.Message,
            "description": "Raised when the username already exists"
        },
        401: {
            "model": misc_models.Message,
            "description": "Raised if the authenticated user is not an admin"
        }
    }
)
async def create_user(
    new_user_data: user_model.UserCreate,
    current_user: user_model.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        return JSONResponse(
            status_code=401,
            content={
                "message": f"You do not have admin permissions which are required to add new users"}
        )
    existing_user = await db["users"].find_one({"username": new_user_data.username})
    if existing_user:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Player {existing_user.username} already exists"}
        )
    user_obj = user_model.UserInDB(
        username=new_user_data.username,
        hashed_password=get_password_hash(new_user_data.password)
    )
    new_user = await db["users"].insert_one(jsonable_encoder(user_obj))
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})
    return created_user
