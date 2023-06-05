import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from requests_ratelimiter import LimiterSession
import time
import re
import json

session = LimiterSession(per_minute=40)
start = time.time()

def get_youtube_link(game_name) -> str:
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
    print(data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"])
    return None

def get_app_information(app_id: int) -> dict:
    response = session.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}")
    data: dict = response.json()
    return data[str(app_id)]

def main():
    response = session.get("http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json")
    data: dict = response.json()
    for app in data["applist"]["apps"]:
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
        youtube_link = get_youtube_link(app_name)
        if youtube_link:
            print(f"{app_id}: {app_name} - {youtube_link}")

if __name__ == "__main__":
    main()

