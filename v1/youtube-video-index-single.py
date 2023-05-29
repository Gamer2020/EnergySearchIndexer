import functions.es_deck_functions
import functions.youtube_functions
import yaml
import os

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(current_dir)

# Open the file using the updated path
config_path = os.path.join(current_dir, 'config.yml')
with open(config_path, 'r') as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

# Access the value of the list in the configuration data
config_es_api_base_url = config_data["config"]["es_api_url"]
config_es_api_version = config_data["config"]["es_api_version"]
config_es_api_full_url = config_es_api_base_url + config_es_api_version + "/"
config_es_api_key = config_data["config"]["es_api_key"]
config_youtube_api_key = config_data["config"]["youtube_api_key"]

video_url = ""

video_info = functions.youtube_functions.get_video_details(
    config_youtube_api_key, video_url
)
# print(video_url)
# print(video_info)
if (
    functions.es_deck_functions.youtube_check_deck_exists(
        video_url, config_es_api_full_url, config_es_api_key
    )
    == False
):
    functions.es_deck_functions.youtube_create_deck(
        video_info, video_url, config_es_api_full_url, config_es_api_key
    )
