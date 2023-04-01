import os
import yaml
import json

def convert_yaml_to_json(yaml_file):
    with open(yaml_file, 'r') as f:
        yaml_data = yaml.safe_load(f)
    app_id = yaml_data['app_id']
    audio_url = yaml_data['audios'][0]['url']
    return {
          str(app_id): {
            'url': audio_url,
            }
      }

if __name__ == '__main__':
    directory = 'games'
    json_data = {
        "app_id": [],
    }
    for file_name in os.listdir(directory):
        if file_name.endswith('.yml'):
            file_path = os.path.join(directory, file_name)
            json_data["app_id"].append(convert_yaml_to_json(file_path))
    with open(os.path.join("v1", 'data.json'), 'w') as f:
        json.dump(json_data, f, indent=2)
        f.write('\n')  # Add a newline character at the end of the file
