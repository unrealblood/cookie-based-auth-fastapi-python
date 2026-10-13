from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from routers.auth_router import verify_access_token
from db.db import User, get_db
from sqlalchemy.orm import Session

user_router = APIRouter()

@user_router.get("/get-me")
def get_me(user_id: int = Depends(verify_access_token), db: Session= Depends(get_db)):
    if not user_id:
        return JSONResponse(status_code=404, content={"message": "Failed to verify token."})

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return JSONResponse(status_code=401, content={"message": "Failed to get user from db."})

    return JSONResponse(status_code=200, content={"message": "User fetched successfully.", "user": {"id": user.id, "name": user.name, "email": user.email}})