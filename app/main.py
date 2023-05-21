import logging
from fastapi import FastAPI
from app.api.youtube import router as youtube_router

logging.basicConfig(level=logging.INFO)


app = FastAPI()


app.include_router(youtube_router, prefix="/api")