from pydantic import BaseModel, HttpUrl


class YoutubeVideoInput(BaseModel):
    video_url: HttpUrl
    
    
class YoutubeVideoCommentsInput(BaseModel):
    video_url: HttpUrl