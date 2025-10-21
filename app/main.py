from fastapi import FastAPI
from app.src.routes import router as events_router

app = FastAPI(title="Assignment 1 FastAPI")

@app.get("/", tags=["Root"], summary="Read Root")
def root():
    return {"message": "Hello, FastAPI is working!"}


app.include_router(events_router, prefix="/events", tags=["Event"])
