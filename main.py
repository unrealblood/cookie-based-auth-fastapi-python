from dotenv import load_dotenv
from fastapi import FastAPI
from os import getenv

load_dotenv()

app = FastAPI()

@app.get("/")
def home():
    return {"message": f"Welcome, Shubham Singh"}