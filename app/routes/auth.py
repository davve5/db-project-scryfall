from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, Field
from db.mongo import MongoManager
from bson.objectid import ObjectId

BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: ObjectId = Field(alias="_id")
    username: str


class UserInDB(User):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    hashed_password: str
    id: ObjectId = Field(alias="_id")

mongo = MongoManager.get_instance()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(id: str):
    user = mongo['users'].find_one({ "_id": ObjectId(id)})
    if user:
        return UserInDB(**user)


def authenticate_user(username: str, password: str):
    user = mongo['users'].find_one({ "username": username})
    user = UserInDB(**user)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user(username: str, password: str):
    password = get_password_hash(password)

    user = mongo['users'].find_one({
        "username": username,
    })

    if user:
        return False

    mongo['users'].insert_one({
        "username": username,
        "hashed_password": password,
    })

    user = mongo['users'].find_one({
        "username": username,
    })

    return UserInDB(**user)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(id=token_data.id)
    if user is None:
        raise credentials_exception
    return user


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")



@router.post("/register")
async def register(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = create_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username already taken",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/reset-password")
async def reset_password(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = mongo['users'].find_one({ "username": form_data.username })
    hashed_password = get_password_hash(form_data.password)
    mongo['users'].update_one({"_id": user.get('_id')}, { "hashed_password": hashed_password })
