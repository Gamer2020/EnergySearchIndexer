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

# Connect to the database
conn = sqlite3.connect(db_file_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Query all entries from the onboarded_channels table
cursor.execute("SELECT * FROM onboarded_channels")
result = cursor.fetchall()

# Extract the channel IDs from the result set and create a list
channel_ids = [row[0] for row in result]

# Close the cursor and the connection
cursor.close()
conn.close()


for channel_id in channel_ids:
    video_urls = functions.youtube_functions.get_video_urls_from_channel_full(
        config_youtube_api_key, channel_id
    )

    for video_url in reversed(video_urls):
        video_info = functions.youtube_functions.get_video_details(
            config_youtube_api_key, video_url
        )
        if (
            functions.es_deck_functions.youtube_check_deck_exists(
                video_url, config_es_api_full_url, config_es_api_key
            )
            == False
        ):
            functions.es_deck_functions.youtube_create_deck(
                video_info, video_url, config_es_api_full_url, config_es_api_key
            )

    if (
        functions.youtube_functions.check_channel_onboarded(channel_id, db_file_path)
        == False
    ):
        functions.youtube_functions.add_channel_to_onboarded(
            channel_id,
            functions.youtube_functions.get_channel_name_from_pending(
                channel_id, db_file_path
            ),
            db_file_path,
        )

    if (
        functions.youtube_functions.check_channel_pending(channel_id, db_file_path)
        == True
    ):
        functions.youtube_functions.delete_channel_pending(
            channel_id,
            db_file_path,
        )
