from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from db.mongo import get_database


class Credentials(BaseModel):
    login: str
    password: str
		
router = APIRouter(
    prefix="/auth",
)

db = get_database()

@router.post("/login", response_model=Credentials)
async def login(credentials: Credentials):
    user = db['users'].find_one({
        "login": credentials.login
    })

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )

    return user


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(credentials: Credentials):
    if len(credentials.login) < 3:
        # raise HTTPException(
        # status_code=status.HTTP,
        # detail=f'File {file.filename} has unsupported extension type',
    # )
        return {"message": "Login has to be at least 3 chars"}

    if len(credentials.password) < 8:
        return {"message": "Password has to be at least 8 chars"}
    
    user = db['users'].find_one({
        "login": credentials.login
    })

    if user is not None: 
        return {"message": "Login is already taken"}

    user = db['users'].insert_one({
        "login": credentials.login,
        "password": credentials.password,
    })

    return {"message": "User created successfuly"}
