from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth_router import auth_router
from routers.user_router import user_router

load_dotenv()

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_headers=["*"], allow_methods=["*"])

app.include_router(auth_router, prefix="/api/auth")
app.include_router(user_router, prefix="/api/users")