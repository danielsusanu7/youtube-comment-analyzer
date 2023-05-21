from fastapi import APIRouter, HTTPException
from app.schemas.youtube_schema import YoutubeVideoInput, YoutubeVideoCommentsInput
from app.services import youtube_service, utils


router = APIRouter()

@router.post("/video_title")
async def get_video_title(input_data: YoutubeVideoInput):
    video_title = youtube_service.get_youtube_video_title(input_data.video_url)
    
    if video_title is None:
        raise HTTPException(
            status_code=422,
            detail="Could not fetch the video title."
        )
        
    return {"title": video_title}

# TODO: endpoint takes too long to run.. why? reply count still all 0, any way to find out if the person who commented is an official one?
@router.post("/video_comments")
async def get_video_comments(input_data: YoutubeVideoCommentsInput):
    video_id = youtube_service.extract_video_id(input_data.video_url)
    
    if video_id is None:
        raise HTTPException(status_code=400, detail="Invalid video URL")
    
    video_info = youtube_service.fetch_video_comments(video_id)
    video_title = youtube_service.get_youtube_video_title(input_data.video_url)
    filename = utils.clean_filename(video_title)
    excel_filename = f"{filename}.xlsx"
    
    df = utils.process_comments_data(video_info["comments"])
    
    output_folder = "data/comments"
    
    utils.save_data_to_excel(df, excel_filename, output_folder)
    
    response_data = {
        "message": f"Successfully fetched {len(video_info['comments'])} comments and replies for '{video_title}'",
        "excel_filename": excel_filename
    }
    
    return response_data