from fastapi import APIRouter, HTTPException
from app.schemas.youtube_schema import YoutubeVideoInput
from app.services.youtube_service import get_youtube_video_title


router = APIRouter()

@router.post("/video_title")
async def get_video_title(input_data: YoutubeVideoInput):
    video_title = get_youtube_video_title(input_data.video_url)
    
    if video_title is None:
        raise HTTPException(
            status_code=422,
            detail="Could not fetch the video title."
        )
        
    return {"title": video_title}