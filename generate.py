import json
import os

import yaml


def convert_yaml_to_json(yaml_file):
    with open(yaml_file, "r") as f:
        yaml_data = yaml.safe_load(f)
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
        app_id, data = convert_yaml_to_json(file_path)
        json_data["app_id"][app_id] = data
    with open(os.path.join("v1", "data.json"), "w") as f:
        json.dump(json_data, f, indent=2)
        f.write("\n")  # Add a newline character at the end of the file
