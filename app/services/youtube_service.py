import logging
import re
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict, List, Union

env_path=Path(os.path.join(os.getcwd(), "app", ".env"))
load_dotenv(dotenv_path=env_path)
logging.basicConfig(level=logging.ERROR)

YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_COMMENT_THREADS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"
YOUTUBE_COMMENTS_URL = "https://www.googleapis.com/youtube/v3/comments"
API_KEY = os.environ["GOOGLE_API_KEY"] # YOUR GOOGLE API KEY


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
    
    response = requests.get(YOUTUBE_VIDEOS_URL, params=params)
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


# def fetch_video_comments(video_id: str) -> Dict[str, List[Dict]]:
#     api_url = YOUTUBE_COMMENT_THREADS_URL
#     comments = []
    
#     next_page_token = None
    
#     while True:
#         params = {
#             "part": "snippet,replies",
#             "videoId": video_id,
#             "key": API_KEY,
#             "maxResults":100,
#             "textFormat":"plainText",
#             "pageToken":next_page_token,
#         }
        
#         response = requests.get(api_url, params=params)
#         data = response.json()
        
#         if response.status_code != 200:
#             logging.warning(f"Error while accessing YouTube API: {response.status_code}")
#             break
        
#         comment_threads = data.get("items", [])
        
#         for thread in comment_threads:
#             top_level_comment = thread["snippet"]["topLevelComment"]
            
#             comments.append({
#                 "comment_id": top_level_comment["id"],
#                 "author": top_level_comment["snippet"]["authorDisplayName"],
#                 "comment": top_level_comment["snippet"]["textDisplay"],
#                 "time": top_level_comment["snippet"]["publishedAt"],
#                 "likes": top_level_comment["snippet"]["likeCount"],
#                 "reply_count": top_level_comment["snippet"].get("totalReplyCount", 0),
#             })
            
#         next_page_token = data.get("nextPageToken")
#         if not next_page_token:
#             break
    
#     logging.info(f"Fetched {len(comments)} comments for video with ID {video_id}")
    
#     return {"video_id": video_id, "comments": comments}


# def fetch_comment_replies(comment_id: str) -> List[Dict]:
#     api_url = YOUTUBE_COMMENTS_URL
#     replies = []
    
#     next_page_token = None
    
#     while True:
#         params={
#             "part": "snippet",
#             "parentId": comment_id,
#             "key": API_KEY,
#             "maxResults": 100,
#             "textFormat": "plainText",
#             "pageToken": next_page_token,
#         }
        
#         response = requests.get(api_url, params=params)
#         data = response.json()
        
#         if response.status_code != 200:
#             logging.warning(f"Error while accessing YouTube API: {response.status_code}")
#             break
        
#         items = data.get("items", [])
        
#         for item in items:
#             snippet = item["snippet"]
#             replies.append({
#                 "reply_author": snippet["authorDisplayName"],
#                 "reply": snippet["textDisplay"],
#                 "published": snippet["publishedAt"],
#                 "updated": snippet["updatedAt"],
#             })
            
#         next_page_token = data.get("nextPageToken")
#         if not next_page_token:
#             break
        
#     return replies
#### ABOVE WORKS, BELOW DOESN'T


def fetch_video_comments_and_replies(video_id: str) -> List[List[str]]:
    result = [['Name', 'Comment', 'Time', 'Likes', 'Reply Count', 'Reply Author', 'Reply', 'Published', 'Updated']]

    next_page_token = None

    while True:
        comments = fetch_video_comments(video_id, next_page_token)

        for comment in comments["comments"]:
            result.append([
                comment["author"],
                comment["comment"],
                comment["time"],
                comment["likes"],
                comment["reply_count"],
                '', '', '', '',
            ])

            if comment["reply_count"] > 0:
                parent = comment["comment_id"]
                next_page_token_rep = None

                while True:
                    reply_data = fetch_comment_replies(parent, next_page_token_rep)

                    for reply in reply_data:
                        result.append([
                            '', '', '', '', '',
                            reply["reply_author"],
                            reply["reply"],
                            reply["published"],
                            reply["updated"],
                        ])

                    next_page_token_rep = reply_data.get("nextPageToken")
                    if not next_page_token_rep:
                        break

        next_page_token = comments.get("nextPageToken")
        if not next_page_token:
            break

    return result


def fetch_video_comments(video_id: str, next_page_token: str = None) -> Dict[str, Union[str, List[Dict]]]:
    api_url = YOUTUBE_COMMENT_THREADS_URL
    comments = []

    params = {
        "part": "snippet,replies",
        "videoId": video_id,
        "key": API_KEY,
        "maxResults": 100,
        "textFormat": "plainText",
        "pageToken": next_page_token,
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    if response.status_code != 200:
        logging.warning(f"Error while accessing YouTube API: {response.status_code}")

    else:
        comment_threads = data.get("items", [])

        for thread in comment_threads:
            top_level_comment = thread["snippet"]["topLevelComment"]

            comments.append({
                "comment_id": top_level_comment["id"],
                "author": top_level_comment["snippet"]["authorDisplayName"],
                "comment": top_level_comment["snippet"]["textDisplay"],
                "time": top_level_comment["snippet"]["publishedAt"],
                "likes": top_level_comment["snippet"]["likeCount"],
                "reply_count": top_level_comment["snippet"].get("totalReplyCount", 0),
            })

    return {"video_id": video_id, "comments": comments, "nextPageToken": data.get("nextPageToken")}


def fetch_comment_replies(comment_id: str, next_page_token: str = None) -> List[Dict]:
    api_url = YOUTUBE_COMMENTS_URL
    replies = []

    params = {
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

    else:
        items = data.get("items", [])

        for item in items:
            snippet = item["snippet"]
            replies.append({
                "reply_author": snippet["authorDisplayName"],
                "reply": snippet["textDisplay"],
                "published": snippet["publishedAt"],
                "updated": snippet["updatedAt"],
            })

    return { "replies": replies, "nextPageToken": data.get("nextPageToken")}


#### THIRD TRY
# def fetch_video_comments_and_replies(video_id: str) -> List[List[str]]:
#     result = [['Name', 'Comment', 'Time', 'Likes', 'Reply Count', 'Reply Author', 'Reply', 'Published', 'Updated']]

#     next_page_token = None

#     while True:
#         comments = fetch_video_comments(video_id, next_page_token)

#         for comment in comments["comments"]:
#             result.append([
#                 comment["author"],
#                 comment["comment"],
#                 comment["time"],
#                 comment["likes"],
#                 '', '', '', '', '',
#             ])

#             if comment["has_replies"]:
#                 parent = comment["comment_id"]
#                 reply_data = fetch_comment_replies(parent)

#                 for reply in reply_data:
#                     result.append([
#                         '', '', '', '', '',
#                         reply["reply_author"],
#                         reply["reply"],
#                         reply["published"],
#                         reply["updated"],
#                     ])

#         next_page_token = comments.get("nextPageToken")
#         if not next_page_token:
#             break

#     return result


# def fetch_video_comments(video_id: str, next_page_token: str = None) -> Dict[str, Union[str, List[Dict]]]:
#     api_url = YOUTUBE_COMMENT_THREADS_URL
#     comments = []

#     params = {
#         "part": "snippet",
#         "videoId": video_id,
#         "key": API_KEY,
#         "maxResults": 100,
#         "textFormat": "plainText",
#         "pageToken": next_page_token,
#     }

#     response = requests.get(api_url, params=params)
#     data = response.json()

#     if response.status_code != 200:
#         logging.warning(f"Error while accessing YouTube API: {response.status_code}")

#     else:
#         comment_threads = data.get("items", [])

#         for thread in comment_threads:
#             top_level_comment = thread["snippet"]["topLevelComment"]
#             has_replies = thread["snippet"]["totalReplyCount"] > 0

#             comments.append({
#                 "comment_id": top_level_comment["id"],
#                 "author": top_level_comment["snippet"]["authorDisplayName"],
#                 "comment": top_level_comment["snippet"]["textOriginal"],
#                 "time": top_level_comment["snippet"]["publishedAt"],
#                 "likes": top_level_comment["snippet"]["likeCount"],
#                 "has_replies": has_replies,
#             })

#     return {"video_id": video_id, "comments": comments, "nextPageToken": data.get("nextPageToken")}


# def fetch_comment_replies(comment_id: str) -> List[Dict]:
#     api_url = YOUTUBE_COMMENT_THREADS_URL
#     replies = []

#     params = {
#         "part": "replies",
#         "id": comment_id,
#         "key": API_KEY,
#         "textFormat": "plainText",
#     }
    
#     response = requests.get(api_url, params=params)
#     data = response.json()

#     if response.status_code != 200:
#         logging.warning(f"Error while accessing YouTube API: {response.status_code}")

#     else:
#         comment_threads = data.get("items", [])

#         for thread in comment_threads:
#             if "replies" in thread and "comments" in thread["replies"]:
#                 for item in thread["replies"]["comments"]:
#                     snippet = item["snippet"]
#                     replies.append({
#                         "reply_author": snippet["authorDisplayName"],
#                         "reply": snippet["textOriginal"],
#                         "published": snippet["publishedAt"],
#                         "updated": snippet["updatedAt"],
#                     })

#     return replies


## CHECKS WHETHER OFFICIAL CHANNEL - TO INCLUDE
YOUTUBE_CHANNELS_URL = 'https://www.googleapis.com/youtube/v3/channels'

def is_official_channel(channel_id: str, api_key):
    api_url = YOUTUBE_CHANNELS_URL

    params = {
        "part": "snippet",
        "id": channel_id,
        "key": api_key,
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    if response.status_code != 200:
        logging.warning(f"Error while accessing YouTube API: {response.status_code}")
        return False

    items = data.get("items", [])

    if len(items) > 0:
        channel_type = items[0]["snippet"].get("channelType")
        if channel_type == "show" or channel_type == "youtube#channel":
            return True

    return False