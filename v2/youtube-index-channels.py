import functions.es_deck_functions
import functions.youtube_functions
import sqlite3
import yaml
import os

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(current_dir)

# Open the file using the updated path
config_path = os.path.join(current_dir, "config.yml")
with open(config_path, "r") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

# Access the value of the list in the configuration data
config_es_api_base_url = config_data["config"]["es_api_url"]
config_es_api_version = config_data["config"]["es_api_version"]
config_es_api_full_url = config_es_api_base_url + config_es_api_version + "/"
config_es_api_key = config_data["config"]["es_api_key"]
config_youtube_api_key = config_data["config"]["youtube_api_key"]

# Create the SQLite database file path using the current directory
db_file_path = os.path.join(current_dir, "youtube.sqlite")


channels = functions.youtube_functions.get_channels_by_game(config_youtube_api_key, "Pokemon Trading Card Game Live")

for channel in channels:
    print(
        f"Channel ID: {channel['channel_id']}, Channel Name: {channel['channel_title']}"
    )
