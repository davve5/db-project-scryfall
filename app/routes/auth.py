from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from db.mongo import MongoManager
from app.utils.jwt import get_password_hash, verify_password, create_access_token


class Credentials(BaseModel):
    login: str
    password: str
		
router = APIRouter()

mongo = MongoManager.get_instance()

@router.post("/login", response_model=Credentials)
async def login(credentials: Credentials):
    user = mongo['users'].find_one({
        "login": credentials.login
    })


    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )
    
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )

    token = create_access_token(credentials.login)

    return token


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(credentials: Credentials):
    if len(credentials.login) < 3:
        return {"message": "Login has to be at least 3 chars"}

    if len(credentials.password) < 8:
        return {"message": "Password has to be at least 8 chars"}
    
    user = mongo['users'].find_one({
        "login": credentials.login
    })

    if user is not None: 
        return {"message": "Login is already taken"}

    password = get_password_hash(password)

    user = mongo['users'].insert_one({
        "login": credentials.login,
        "password": password,
    })

    return {"message": "User created successfuly"}
