import logging
import re
import requests
import pandas as pd
from typing import Optional, Dict, List

logging.basicConfig(level=logging.ERROR)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"
API_KEY = "" # YOUR GOOGLE API KEY


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


def fetch_video_comments(video_id: str) -> Dict[str, List[Dict]]:
    api_url = "https://www.googleapis.com/youtube/v3/commentThreads"
    comments = []
    
    next_page_token = None
    
    while True:
        params = {
            "part": "snippet,replies",
            "videoId": video_id,
            "key": API_KEY,
            "maxResults":100,
            "textFormat":"plainText",
            "pageToken":next_page_token,
        }
        
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if response.status_code != 200:
            logging.warning(f"Error while accessing YouTube API: {response.status_code}")
            break
        
        comment_threads = data.get("items", [])
        
        for thread in comment_threads:
            top_level_comment = thread["snippet"]["topLevelComment"]
            replies = thread["replies"]["comments"] if "replies" in thread else []
            
            comments.append({
                "comment_id": top_level_comment["id"],
                "author": top_level_comment["snippet"]["authorDisplayName"],
                "comment": top_level_comment["snippet"]["textDisplay"],
                "time": top_level_comment["snippet"]["publishedAt"],
                "likes": top_level_comment["snippet"]["likeCount"],
                "reply_count": top_level_comment["snippet"].get("totalReplyCount", 0),
                # "replies": [
                #     {
                #         "reply_id": reply["id"],
                #         "reply_author": reply["snippet"]["authorDisplayName"],
                #         "reply": reply["snippet"]["textDisplay"],
                #         "published": reply["snippet"]["publishedAt"],
                #         "updated": reply["snippet"]["updatedAt"]
                #     }
                #     for reply in replies
                # ]
            })
            
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
    
    logging.info(f"Fetched {len(comments)} comments for video with ID {video_id}")
    
    return {"video_id": video_id, "comments": comments}


def fetch_comment_replies(comment_id: str) -> List[Dict]:
    api_url = "https://www.googleapis.com/youtube/v3/comments"
    replies = []
    
    next_page_token = None
    
    while True:
        params={
            "part": "snippet",
            "parentId": comment_id,
            "key": API_KEY,
            "maxResults": 100,
            "textFormat": "plainText",
            "pageToken": next_page_token,
        }
        
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if response.status_code != 200:
            logging.warning(f"Error while accessing YouTube API: {response.status_code}")
            break
        
        items = data.get("items", [])
        
        for item in items:
            snippet = item["snippet"]
            replies.append({
                "reply_author": snippet["authorDisplayName"],
                "reply": snippet["textDisplay"],
                "published": snippet["publishedAt"],
                "updated": snippet["updatedAt"],
            })
            
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
        
    return replies
