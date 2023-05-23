import os
import re
import pandas as pd
from app.services.youtube_service import fetch_video_comments_and_replies

def clean_filename(filename: str, replace_with="_") -> str:
    pattern = r'[<>:"/\\|?*]'
    
    cleaned_filename = re.sub(pattern, replace_with, filename)
    
    return cleaned_filename


# def process_comments_data(comments_data: list) -> pd.DataFrame:
#     df_data = []
    
#     for comment in comments_data:
#         comment_row = [
#             comment["author"],
#             comment["comment"],
#             comment["time"],
#             comment["likes"],
#             comment["reply_count"],
#             None,  # Placeholder for reply_author
#             None,  # Placeholder for reply
#             None,  # Placeholder for published
#             None  # Placeholder for updated
#         ]
        
#         df_data.append(comment_row)
        
#         replies = fetch_comment_replies(comment["comment_id"])
#         for reply in replies:
#             reply_row = [
#                 None,  # Placeholder for author
#                 None,  # Placeholder for comment
#                 None,  # Placeholder for time
#                 None,  # Placeholder for likes
#                 None,  # Placeholder for reply_count
#                 reply["reply_author"], 
#                 reply["reply"],
#                 reply["published"],
#                 reply["updated"]
#             ]
            
#             df_data.append(reply_row)
        
#     columns = [
#         "Name",
#         "Comment",
#         "Time",
#         "Likes",
#         "Reply Count",
#         "Reply Author",
#         "Reply",
#         "Published",
#         "Updated"
#     ]
    
#     return pd.DataFrame(df_data, columns=columns)



def process_comments_data(video_id: str) -> pd.DataFrame:
    comments_and_replies = fetch_video_comments_and_replies(video_id)
    columns = [
        "Name",
        "Comment",
        "Time",
        "Likes",
        "Reply Count",
        "Reply Author",
        "Reply",
        "Published",
        "Updated"
    ]
    
    return pd.DataFrame(comments_and_replies[1:], columns=columns)

# def process_comments_data(video_id: str) -> pd.DataFrame:
#     comments_and_replies = fetch_video_comments_and_replies(video_id)
#     columns = [
#         "Name",
#         "Comment",
#         "Time",
#         "Likes",
#         "Reply Count",
#         "Reply Author",
#         "Reply",
#         "Published",
#         "Updated"
#     ]

#     return pd.DataFrame(comments_and_replies[1:], columns=columns)


def save_data_to_excel(df: pd.DataFrame, filename: str, output_folder: str) -> None:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    file_path = os.path.join(output_folder, filename)
    df.to_excel(file_path, index=False)