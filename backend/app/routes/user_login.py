from pydantic import BaseModel
from src.core.user_manager import UserManager
from fastapi import APIRouter, HTTPException
from app.middleware.jwt_auth import create_access_token
from utils.logger import get_logger

router = APIRouter()
user_manager = UserManager()
logger = get_logger(__name__)


class LoginRequest(BaseModel):
    username: str
    enc_password: str

class SignupRequest(BaseModel):
    username: str
    enc_password: str
    firstname: str
    lastname: str


@router.post("/login")
def login(request: LoginRequest):
    logger.info(f"Login attempt for user: {request.username}")
    user_details = user_manager.get_user_details(request.username)
    if user_details["status"] == "fail":
        logger.warning(f"Login failed: user not found ({request.username})")
        raise HTTPException(status_code=404, detail=user_details["message"])
    if user_details["data"]["enc_password"] == request.enc_password:
        logger.info(f"Login successful for user: {request.username}")
        token = create_access_token(data={"sub": request.username})
        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
        }
    else:
        logger.warning(f"Login failed: invalid credentials for {request.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/signup")
def signup(request: SignupRequest):
    logger.info(f"Signup attempt for user: {request.username}")
    create_status = user_manager.create_user(
        request.username, request.username, request.enc_password,
        request.firstname, request.lastname
    )
    if create_status["status"] == "fail":
        logger.warning(f"Signup failed for {request.username}: {create_status['message']}")
        raise HTTPException(status_code=400, detail=create_status["message"])
    
    logger.info(f"Signup successful for user: {request.username}")
    token = create_access_token(data={"sub": request.username})
    return {
        "message": create_status["message"],
        "access_token": token,
        "token_type": "bearer",
    }
