import os
import jwt
from datetime import datetime, timedelta
from typing import Any
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret123")

# def get_token_from_request(request):
#     if "Authorization" not in request.headers:
#         return False
#     token_header = request.headers["Authorization"]
#     if token_header.startswith("Bearer "):
#         return token_header.split("Bearer ")[-1]

# def verify_access_token(request):
#     token = get_token_from_request(request)
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {"exp": expire, "sub": str(subject)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)