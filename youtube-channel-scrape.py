import functions.youtube_functions
import yaml

# Read the configuration data from the file
with open("config.yml") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

# Access the value of the list in the configuration data

print(config_data)

config_es_api_url = config_data["config"]["es_api_url"]
config_es_api_version = config_data["config"]["es_api_version"]
config_es_api_key = config_data["config"]["es_api_key"]
config_youtube_api_key = config_data["config"]["youtube_api_key"]

config_youtube_channels = config_data["config"]["youtube_channels"]

video_urls = functions.youtube_functions.get_video_urls_from_channel_list(
    config_youtube_api_key,config_youtube_channels
)
print(video_urls)
