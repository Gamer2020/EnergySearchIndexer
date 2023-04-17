import functions.es_deck_functions
import functions.youtube_functions
import yaml

# Read the configuration data from the file
with open("config.yml") as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

# Access the value of the list in the configuration data
config_es_api_base_url = config_data["config"]["es_api_url"]
config_es_api_version = config_data["config"]["es_api_version"]
config_es_api_full_url = config_es_api_base_url + config_es_api_version + "/"
config_es_api_key = config_data["config"]["es_api_key"]
config_youtube_api_key = config_data["config"]["youtube_api_key"]

config_youtube_channels = config_data["config"]["youtube_channels_xml"]

all_video_data = functions.youtube_functions.get_video_urls_from_channel_list_xml(
    config_youtube_channels
)
for video_data in all_video_data:
    print(f"Video Title: {video_data['video_title']}")
    print(f"Video URL: {video_data['video_url']}")
    print(f"Channel Title: {video_data['channel_title']}")
    print(f"Channel URL: {video_data['channel_url']}")
    print(f"Publish Date: {video_data['publish_date']}")
    print(f"Video Description: {video_data['video_description']}")
    print()

# for video_url in video_urls:
#     video_info = functions.youtube_functions.get_video_details(
#         config_youtube_api_key, video_url
#     )
#     print(video_url)
#     print(video_info)
#     if (
#         functions.es_deck_functions.youtube_check_deck_exists(
#             video_url, config_es_api_full_url, config_es_api_key
#         )
#         == False
#     ):
#         functions.es_deck_functions.youtube_create_deck(
#             video_info, video_url, config_es_api_full_url, config_es_api_key
#         )
