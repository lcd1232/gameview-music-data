import argparse
import os
import time
import typing

import yaml
from pytube import Search
from requests_ratelimiter import LimiterSession

session = LimiterSession(per_minute=40)
start = time.time()


def write_to_file(gameid: str, game_name: str, youtube_link: str) -> None:
    with open(os.path.join("games", f"{gameid}.yml"), "w") as f:
        yaml.dump(
            {
                "app_id": gameid,
                "name": game_name,
                "audios": [
                    {
                        "url": youtube_link,
                    },
                ],
            },
            f,
            sort_keys=False,
            explicit_start=True,
        )


def get_youtube_link(game_name) -> typing.Optional[str]:
    search_query = f"{game_name} main theme"
    s = Search(search_query)

    if len(s.results) == 0:
        print(f"Failed to find any results for {game_name}")
        return None

    for result in s.results:
        if not result.length:
            continue
        if result.length > 300:
            print(
                f"Skipping too long video: {result.video_id} ({result.length}) - {result.title}"
            )
            continue
        return result.watch_url
    return None


def get_app_information(app_id: int) -> dict:
    response = session.get(
        f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    )
    data: dict = response.json()
    return data[str(app_id)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=None, help="Start from this appid")
    args = parser.parse_args()
    passed: bool = False

    response = session.get(
        "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
    )
    data: dict = response.json()
    print(f"Found {len(data['applist']['apps'])} apps")
    # Sort the apps by appid descending
    data["applist"]["apps"].sort(key=lambda x: x["appid"])
    for i, app in enumerate(data["applist"]["apps"]):
        if args.start is not None:
            if not passed:
                if app["appid"] == args.start:
                    print(f"Skipped {i} apps")
                    passed = True
                else:
                    continue
        print(f"Checking {app['appid']} - {app['name']}")
        app_id = app["appid"]
        app_name = app["name"]
        if os.path.exists(os.path.join("games", f"{app_id}.yml")):
            print(f"Skipping {app_id} - {app_name} since it already exists")
            continue
        app_information = get_app_information(app_id)
        if not app_information["success"]:
            print(f"Failed to get information for {app_id} - {app_name}")
            continue
        if not app_information["data"]["type"] == "game":
            continue
        print(f"Found {app_id} - {app_name}")
        youtube_link = get_youtube_link(app_name)
        if youtube_link:
            write_to_file(app_id, app_name, youtube_link)
            print(f"Wrote {app_id} - {app_name}")


if __name__ == "__main__":
    main()
    # s = Search("zelda live")
    # print(len(s.results))
    # for result in s.results:
    #     print(result, result.title, result.length, result.metadata)
