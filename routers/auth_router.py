from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Depends, Cookie, HTTPException, status
from schemas.auth_schema import RegisterModel, LoginModel
from sqlalchemy.orm import Session
from db.db import get_db, User
import bcrypt
import jwt
from os import getenv
from dotenv import load_dotenv

load_dotenv()

auth_router = APIRouter()

@auth_router.post("/register")
def register(user: RegisterModel, db: Session = Depends(get_db)):
    if user.name == "":
        return JSONResponse(status_code=400, content={"message": "name field is empty"})

    if user.email == "":
        return JSONResponse(status_code=400, content={"message": "email field is empty"})

    if user.password == "":
        return JSONResponse(status_code=400, content={"message": "password field is empty"})

    # hash password
    password_bytes = user.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))

    new_user = User(name= user.name, email= user.email, password= hashed_password.decode('utf-8'))

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        return JSONResponse(status_code=409, content={"message": "Email address already exists."})

    return JSONResponse(status_code=201, content={"message": "User registered successfully, you may now login."})

@auth_router.post("/login")
def login(user: LoginModel, db: Session = Depends(get_db)):
    if user.email == "":
            return JSONResponse(status_code=400, content={"message": "email field is empty"})
    
    if user.password == "":
        return JSONResponse(status_code=400, content={"message": "password field is empty"})

    # check for user in db
    fetched_user = db.query(User).filter(User.email == user.email).first()

    if not fetched_user:
        return JSONResponse(status_code=404, content={"message": "User not found."})

    # check password
    user_password_bytes = user.password.encode('utf-8')
    fetched_user_password_bytes = fetched_user.password.encode('utf-8')
    
    is_valid_password = bcrypt.checkpw(user_password_bytes, fetched_user_password_bytes)

    if not is_valid_password:
        return JSONResponse(status_code=400, content={"message": "Invalid credentials."})

    # generate access token
    access_token = jwt.encode({"id": fetched_user.id}, getenv("JWT_SECRET"), algorithm="HS256")

    # 1. Create the response object
    json_response = JSONResponse(
        status_code=200,
        content={
            "message": "Login successful.",
            "user": {"id": fetched_user.id, "name": fetched_user.name, "email": fetched_user.email},
        },
    )

    # 2. Attach the cookie directly to it
    json_response.set_cookie(
        key="access_token",
        value=access_token,
        secure=True,
        httponly=True,
        samesite="none",
        max_age=3600 * 24 * 7,  # 7 days
    )

    return json_response

@auth_router.post("/logout")
def logout():
    json_response = JSONResponse(
        status_code=200,
        content={"message": "Logout successfull."}
    )

    json_response.delete_cookie(
        key="access_token",
        secure=True,
        httponly=True,
        samesite="none"
    )

    return json_response

def verify_access_token(access_token: str | None = Cookie(default= None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found",
        )

    try:
        decoded = jwt.decode(
            access_token,
            getenv("JWT_SECRET"),
            algorithms=["HS256"],
        )
        return int(decoded["id"])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )