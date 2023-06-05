import json
import os
import typing

import yaml


def convert_yaml_to_json(yaml_data) -> typing.Tuple[str, typing.Dict[str, str]]:
    app_id = yaml_data["app_id"]
    audio_url = yaml_data["audios"][0]["url"]
    return str(app_id), {
        "url": audio_url,
    }


if __name__ == "__main__":
    directory = "games"
    json_data = {
        "app_id": {},
    }
    files = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".yml"):
            files.append(file_name)
    files.sort()
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        with open(file_path, "r") as f:
            yaml_data = yaml.load(f)
        if yaml_data["no_soundtrack"]:
            # This game might be so unpopular or outdated that it doesn't have a soundtrack
            continue
        app_id, data = convert_yaml_to_json(file_path)
        json_data["app_id"][app_id] = data
    with open(os.path.join("v1", "data.json"), "w") as f:
        json.dump(json_data, f, separators=(",", ":"))
        f.write("\n")  # Add a newline character at the end of the file
