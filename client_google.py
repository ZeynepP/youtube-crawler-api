import json
import requests
from bs4 import BeautifulSoup
from ebbe import getpath
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
import time
from exceptions import YouTubeAccessNotConfiguredError, YouTubeDisabledCommentsError, YouTubeExclusiveMemberError, YouTubeInvalidVideoTargetError
from utils import create_pool_manager, seconds_to_midnight_pacific_time
from googleapiclient.discovery import build

YOUTUBE_API_MAX_VIDEOS_PER_CALL = 50
YOUTUBE_API_MAX_CHANNELS_PER_CALL = 50
YOUTUBE_API_MAX_COMMENTS_PER_CALL = 100
from datetime import  datetime

class YouTubeAPIClientGoogle(object):
    def __init__(self, key, logging):
        if not isinstance(key, list):
            key = [key]
        self.debug = False
        self.keys = {k: True for k in key}
        self.current_key = key[0]
        logging.info(" Key : " + self.current_key)
        self.pool_manager = create_pool_manager()
        self.logging = logging

        self.youtube = build('youtube', 'v3', developerKey=self.current_key, cache_discovery=False)

    def rotate_key(self):
        self.keys[self.current_key] = False

        available_key = next(
            (key for key, available in self.keys.items() if available), None
        )

        if available_key:
            self.current_key = available_key
            self.logging.debug(" Key : " + self.current_key)
            self.youtube = build('youtube', 'v3', developerKey=self.current_key, cache_discovery=False)
            return True

        self.current_key = None

        return False

    def reset_keys(self):
        for key in self.keys:
            if self.current_key is None:
                self.current_key = key
                self.logging.debug("Changing key : " + key)

        self.keys[key] = True

    def scrap_channel_id(self, url):
        soup = BeautifulSoup(requests.get(url).text,  "html.parser")
        span_tag = soup.find('span', {'itemprop': 'author'})
        if span_tag:
            link_tag = span_tag.find('link', {'itemprop': 'url'})
            return link_tag['href'] if link_tag else None
        return None

    def get_channel_video_ids(self, channel_id, published_after, published_before, next_page_token=None):
        ids = []
        while 1:  # to gel all pages
            while True:  # to get res
                try:
                    res = self.youtube.search().list(part="snippet",
                                                     maxResults=YOUTUBE_API_MAX_VIDEOS_PER_CALL,
                                                     channelId=channel_id,
                                                     type="video",
                                                     publishedBefore=published_before,
                                                     publishedAfter=published_after,
                                                     order="date",
                                                     pageToken=next_page_token).execute()
                    break
                except HttpError as e:
                    if e.resp.status == 403:
                        data = json.loads(
                            e.content)  # This might need json.loads depending on the exact client library/version
                        reason = getpath(data, ["error", "errors", 0, "reason"])
                        self.logging.warn(reason)
                        if reason == "accessNotConfigured":
                            raise YouTubeAccessNotConfiguredError(e.uri)
                        elif reason == "commentsDisabled":
                            raise YouTubeDisabledCommentsError(e.uri)
                        elif reason == "forbidden":
                            raise YouTubeExclusiveMemberError(e.uri)
                        elif reason == "quotaExceeded":
                            if not self.rotate_key():
                                self.logging.warn(
                                    "YouTube API limits reached for every key. Will now wait until midnight Pacific time!",
                                    extra={
                                        "source": "YouTubeAPIClient",
                                        "sleep_time": 1,
                                    },
                                )
                                sleep_time = seconds_to_midnight_pacific_time() + 10
                                time.sleep(sleep_time)
                                self.reset_keys()


            for item in res["items"]:
                ids.append(item["id"]["videoId"])
                # if item["id"]["kind"] == "youtube#video":
                #     if item["snippet"]["channelId"] == channel_id:  # checking if the same channel because it is query search
                #         ids.append(item["id"]["videoId"])

            next_page_token = res.get('nextPageToken')

            if next_page_token is None:
                break
        return ids


    def get_playlist_video_ids(self, playlist_id, next_page_token=None):
        ids = []
        while 1:  # to gel all pages
            while True:  # to get res
                try:
                    res = self.youtube.playlistItems().list(part="contentDetails",
                                                     maxResults=YOUTUBE_API_MAX_VIDEOS_PER_CALL,
                                                     playlistId=playlist_id,
                                                     pageToken=next_page_token).execute()
                    break
                except HttpError as e:
                    if e.resp.status == 403:
                        data = json.loads(
                            e.content)  # This might need json.loads depending on the exact client library/version
                        reason = getpath(data, ["error", "errors", 0, "reason"])
                        self.logging.warn(reason)
                        if reason == "accessNotConfigured":
                            raise YouTubeAccessNotConfiguredError(e.uri)
                        elif reason == "commentsDisabled":
                            raise YouTubeDisabledCommentsError(e.uri)
                        elif reason == "forbidden":
                            raise YouTubeExclusiveMemberError(e.uri)
                        elif reason == "quotaExceeded":
                            if not self.rotate_key():
                                self.logging.warn(
                                    "YouTube API limits reached for every key. Will now wait until midnight Pacific time!",
                                    extra={
                                        "source": "YouTubeAPIClient",
                                        "sleep_time": 1,
                                    },
                                )
                                sleep_time = seconds_to_midnight_pacific_time() + 10
                                time.sleep(sleep_time)
                                self.reset_keys()



            for item in res["items"]:
                ids.append(item["contentDetails"])
                # if item["id"]["kind"] == "youtube#video":
                #     if item["snippet"]["channelId"] == channel_id:  # checking if the same channel because it is query search
                #         ids.append(item["id"]["videoId"])

            next_page_token = res.get('nextPageToken')

            if next_page_token is None:
                break
        return ids

    def get_data_video(self, video_ids):
        all_videos = []
        while True:
            try:
                request = self.youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=",".join(video_ids)
                )
                results = request.execute()
                break
            except HttpError as e:
                if e.resp.status == 403:
                    data = json.loads(
                        e.content)  # This might need json.loads depending on the exact client library/version
                    reason = getpath(data, ["error", "errors", 0, "reason"])

                    if reason == "accessNotConfigured":
                        raise YouTubeAccessNotConfiguredError(e.uri)
                    elif reason == "commentsDisabled":
                        raise YouTubeDisabledCommentsError(e.uri)
                    elif reason == "forbidden":
                        raise YouTubeExclusiveMemberError(e.uri)
                    elif reason == "quotaExceeded":
                        if not self.rotate_key():
                            self.logging.warn(
                                "YouTube API limits reached for every key. Will now wait until midnight Pacific time!",
                                extra={
                                    "source": "YouTubeAPIClient",
                                    "sleep_time": 1,
                                },
                            )
                            sleep_time = seconds_to_midnight_pacific_time() + 10
                            time.sleep(sleep_time)
                            self.reset_keys()

        for item in results["items"]:
            video_id = item["id"]

            data = {}
            data["data"] = {}
            data["data"]["video"] = item
            language = "en"
            if "fr" in item["snippet"].get("defaultLanguage", "en"):
                language = "fr"
            data["data"]["captions"] = self.captions(video_id, language)

            try:

                comment_count = int(item["statistics"].get("commentCount", 0))
                if comment_count > 0:
                    data["data"]["comments"] = self.get_comments(video_id)

            except Exception as ex:
                self.logging(ex, video_id + " is colased to comments")
                pass

            all_videos.append(data)

        return all_videos

    def get_comments(self, video_id):
        if video_id is None:
            raise YouTubeInvalidVideoTargetError
        pagetoken = None
        comments = []

        while True:  # for paging
            while 1:  # for quota etc.
                try:
                    result = self.youtube.commentThreads().list(
                        part='snippet, replies',
                        videoId=video_id,
                        maxResults=100,  # Adjust the number as needed
                        pageToken=pagetoken,
                        order='relevance',
                    ).execute()
                    break
                except HttpError as e:
                    if e.resp.status == 403:
                        data = json.loads(
                            e.content)  # This might need json.loads depending on the exact client library/version
                        reason = getpath(data, ["error", "errors", 0, "reason"])

                        if reason == "accessNotConfigured":
                            raise YouTubeAccessNotConfiguredError(e.uri)
                        elif reason == "commentsDisabled":
                            raise YouTubeDisabledCommentsError(e.uri)
                        elif reason == "forbidden":
                            raise YouTubeExclusiveMemberError(e.uri)
                        elif reason == "quotaExceeded":
                            if not self.rotate_key():
                                self.logging.warn(
                                    "YouTube API limits reached for every key. Will now wait until midnight Pacific time!",
                                    extra={
                                        "source": "YouTubeAPIClient",
                                        "sleep_time": 1,
                                    },
                                )
                                sleep_time = seconds_to_midnight_pacific_time() + 10
                                time.sleep(sleep_time)
                                self.reset_keys()

            pagetoken = result.get("nextPageToken")
            comments.extend(result["items"])
            if len(comments) > 100 or pagetoken is None or len(result["items"]) == 0:
                break

        return comments

    def captions(self, video_id, language="en"):
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        except Exception as ex:
            return {"error": str(ex)}
