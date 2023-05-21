import logging
import re
import requests
from typing import Optional

logging.basicConfig(level=logging.ERROR)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"
API_KEY = "AIzaSyAiF6PLsdexy2O0q2NoxzBKZ1R8sVb3Bmg"


def extract_video_id(url: str) -> Optional[str]:
    pattern = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([-_A-Za-z0-9]{11})"
    match = re.search(pattern, url)
    
    if match:
        logging.info(f"Extracted Video ID: {match.group(1)}")
        return match.group(1)
    return None


def fetch_video_title(video_id: str) -> Optional[str]:
    params = {
        "part": "snippet",
        "id": video_id,
        "key": API_KEY,
    }
    
    response = requests.get(YOUTUBE_API_URL, params=params)
    data = response.json()
    
    logging.info(f"API Response: {data}")
    
    if response.status_code != 200:
        logging.error(f"Error while accessing API: {response.status_code} - {response.text}")
        return None
    
    if "items" not in data or len(data["items"]) == 0:
        return None
    
    return data["items"][0]["snippet"]["title"]


def get_youtube_video_title(video_url: str) -> Optional[str]:
    logging.info(f"Processing Video URL: {video_url}")
    
    video_id = extract_video_id(video_url)
    
    if video_id is None:
        logging.warning("Could not extract video ID from URL")
        return None
    
    title = fetch_video_title(video_id)

    if title:
        logging.info(f"Retrieved Video Title: {title}")
    else:
        logging.warning("Could not fetch video title from API")

    return title