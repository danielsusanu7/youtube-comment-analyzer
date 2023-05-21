from pydantic import BaseModel, HttpUrl


class YoutubeVideoInput(BaseModel):
    video_url: HttpUrl