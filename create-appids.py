import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from requests_ratelimiter import LimiterSession
import time
import re
import json
import datetime
import typing
import yaml
import os
import argparse

session = LimiterSession(per_minute=40)
start = time.time()

def write_to_file(gameid: str, game_name: str, youtube_link: str) -> None:
    with open(os.path.join("games", f"{gameid}.yml"), "w") as f:
        yaml.dump({
            "app_id": gameid,
            "name": game_name,
            "audios": [
                {
                    "url": youtube_link,
                },
            ],
        }, f, sort_keys=False, explicit_start=True)

def text_to_timedelta(text: str) -> datetime.timedelta:
    splits = text.split(":")
    if len(splits) == 2:
        minutes, seconds = splits
        return datetime.timedelta(minutes=int(minutes), seconds=int(seconds))
    elif len(splits) == 3:
        hours, minutes, seconds = splits
        return datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
    else:
        raise ValueError(f"Invalid time format: {text}")

def get_youtube_link(game_name) -> typing.Optional[str]:
    search_query = f"{game_name} main theme"
    search_query_encoded = quote(search_query)

    # Search on YouTube
    youtube_url = f"https://www.youtube.com/results?search_query={search_query_encoded}&sp=QgIIAQ%3D%3D"

    # Fetch YouTube search results
    response = requests.get(youtube_url)
    result = re.findall(r"ytInitialData\s*=\s*({.*?});", response.text)
    if not result:
        return None
    data = result[0]
    data = json.loads(data)
    for content in data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]:
        if "itemSectionRenderer" in content:
            for item in content["itemSectionRenderer"]["contents"]:
                if "videoRenderer" in item:
                    video = item["videoRenderer"]
                    if "lengthText" not in video:
                        print(f"Skipping video since it's live - {video['videoId']}")
                        continue
                    duration = text_to_timedelta(video["lengthText"]["simpleText"])
                    video_id = video["videoId"]
                    if duration.seconds == 0:
                        print(f"Skipping video with empty length - {video_id}")
                        continue
                    if duration > datetime.timedelta(minutes=5):
                        print(f"Skipping video with length > 5 minutes - {video_id}")
                        continue
                    return f"https://www.youtube.com/watch?v={video_id}"
    return None

def get_app_information(app_id: int) -> dict:
    response = session.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}")
    data: dict = response.json()
    return data[str(app_id)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=None, help="Start from this appid")
    args = parser.parse_args()
    passed: bool = False

    response = session.get("http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json")
    data: dict = response.json()
    for app in data["applist"]["apps"]:
        if args.start is not None:
            if not passed:
                if app["appid"] == args.start:
                    passed = True
                else:
                    continue
        print(f"Checking {app['appid']} - {app['name']}")
        app_id = app["appid"]
        app_name = app["name"]
        app_information = get_app_information(app_id)
        if not app_information["success"]:
            print(f"Failed to get information for {app_id} - {app_name}")
            continue
        if not app_information["data"]["type"] == "game":
            continue
        print(f"Found {app_id} - {app_name}")
        if os.path.exists(os.path.join("games", f"{app_id}.yml")):
            print(f"Skipping {app_id} - {app_name} since it already exists")
            continue
        youtube_link = get_youtube_link(app_name)
        if youtube_link:
            write_to_file(app_id, app_name, youtube_link)
            print(f"Wrote {app_id} - {app_name}")

if __name__ == "__main__":
    main()

