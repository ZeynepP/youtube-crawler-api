
import logging.config
import os
from datetime import datetime

from utils import dump_crawled_videos, get_crawled_videos
from client_google import YouTubeAPIClientGoogle
from utils import divide_chunks
from write import generate_file_name, write_raw_list

logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("s3transfer").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)
logging.getLogger("googleapiclient.discovery").setLevel(logging.WARNING)

def get_video_ids(name, client, video_filter, published_after, published_before):
    ids = []
    if name.startswith("UC"):  # user channel
        id = name
    else:
        name = "https://www.youtube.com/@" + name
        id = client.scrap_channel_id(name)  # cheaper than #channel_id = client.get_channel_id(seed[-1])
    if id:
        channel_id = id.split("/")[-1]
        items = client.get_channel_video_ids(channel_id, published_after, published_before)
        for item in items:
            if item not in video_filter:
                ids.append(item)
    return ids


def youtube_crawler(playlists, video_ids, published_after, published_before, tokens):

    client = YouTubeAPIClientGoogle(tokens, logger)


    try:
        video_filter = get_crawled_videos("youtube.meta", "data")
    except:
        video_filter = []

    if published_before:
        published_before = datetime.fromisoformat(published_before)
    if published_after:
        published_after = datetime.fromisoformat(published_after)



    if len(video_ids) > 0:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data","youtube_data.jsonl")
        video_ids = video_ids.strip().split(",")
        videos = client.get_data_video(video_ids)
        write_raw_list(file_path, videos)
        dump_crawled_videos(video_ids, "youtube.meta", "data")

    elif playlists: #it means it is a playlist
        for playlist in playlists.split(","):
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",
                                     generate_file_name(platform="youtube",
                                                        start_date=published_after,
                                                        end_date=published_before))
            video_ids = get_video_ids(
                        name=playlist,
                        client=client,
                        video_filter = video_filter,
                        published_after=published_after.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        published_before=published_before.strftime("%Y-%m-%dT%H:%M:%SZ")
                    )
            logger.debug(
                f"For Youtube playlist {playlist}   ids : {len(video_ids)} from {published_after.strftime('%Y-%m-%d')} to {published_before.strftime('%Y-%m-%d')}")
            #to make request in chunks we can send max 50 ids
            video_ids_chunks = divide_chunks(video_ids, 50)
            for chunk_ids in video_ids_chunks:
                videos= client.get_data_video(chunk_ids)
                write_raw_list(file_path, videos)
            dump_crawled_videos(video_ids, "youtube.meta", "data")

    else:
        logging.error("!! No playlist No video id !! Nothing to do !! Exit !!")
        exit()

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Starting YouTube crawler")
    playlists = input("Enter comma seperated playlists or handles / empty: ")
    video_ids = input("Enter comma seperated video ids / no need if playlists provided: ")
    published_after = input("Enter start date YYYY-MM-DD: ")
    published_before = input("Enter end date YYYY-MM-DD: ")
    tokens = input("Enter comma seperated tokens: ")
    youtube_crawler(playlists, video_ids, published_after, published_before, tokens)


