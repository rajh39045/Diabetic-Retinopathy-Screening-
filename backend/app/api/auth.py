
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import jwt

from app.database.mongodb import db
from app.api.deps import get_current_user
from app.api.auth_config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(prefix="/api/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = "HEALTHCARE_WORKER"


class RegisterResponse(BaseModel):
    message: str
    user_id: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user_id: str
    role: str
    name: str
    email: str


def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register_user(data: RegisterRequest):
    role = data.role.upper().strip()
    if role not in {"HEALTHCARE_WORKER", "OPHTHALMOLOGIST"}:
        raise HTTPException(400, "Invalid role")

    if await db.users.find_one({"email": data.email.lower()}):
        raise HTTPException(409, "Email already registered")

    user = {
        "name": data.name.strip(),
        "email": data.email.lower(),
        "password": pwd_context.hash(data.password),
        "role": role,
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.users.insert_one(user)
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
    }


@router.post("/login", response_model=LoginResponse)
async def login_user(data: LoginRequest):
    user = await db.users.find_one({"email": data.email.lower()})

    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
    })

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user["_id"]),
        "role": user["role"],
        "name": user["name"],
        "email": user["email"],
    }


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user


@router.post("/logout")
async def logout():
    # JWT is stateless; client removes the token.
    return {"message": "Logout successful"}
