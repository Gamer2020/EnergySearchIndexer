import yaml
import sqlite3
import os

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(current_dir)

# Open the file using the updated path
config_path = os.path.join(current_dir, "config.yml")

with open(config_path, "r") as config_file:
    yaml_data = yaml.safe_load(config_file)

#######################################
#            YouTube - START
#######################################

# Get the preloaded_channels from the YAML data
preloaded_channels = yaml_data["config"]["preloaded_channels"]

# Connect to the main YouTube database (creates a new file if it doesn't exist)
conn = sqlite3.connect("youtube.sqlite")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the onboarded_channels table if it doesn't exist
cursor.execute(
    """CREATE TABLE IF NOT EXISTS onboarded_channels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )"""
)

# Insert or update preloaded_channels in the onboarded_channels table
for channel in preloaded_channels:
    channel_parts = channel.split("|")
    if len(channel_parts) >= 2:
        channel_id = channel_parts[0].strip()
        channel_name = channel_parts[1].strip()
        cursor.execute(
            "INSERT OR REPLACE INTO onboarded_channels (id, name) VALUES (?, ?)",
            (channel_id, channel_name),
        )

# Create the pending_channels table if it doesn't exist
cursor.execute(
    """CREATE TABLE IF NOT EXISTS pending_channels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )"""
)

# Commit the changes and close the connection
conn.commit()
conn.close()

#######################################
#             YouTube - END
#######################################


#######################################
#          Cache - START
#######################################

# Connect to the cache database (creates a new file if it doesn't exist)
cache_conn = sqlite3.connect("youtube_cache.sqlite")

# Create a cursor object to execute SQL commands
cache_cursor = cache_conn.cursor()

# Create the youtube_cache table if it doesn't exist
cache_cursor.execute(
    """CREATE TABLE IF NOT EXISTS youtube_cache (
        request_hash TEXT PRIMARY KEY,
        response_json TEXT,
        timestamp INTEGER
    )"""
)

# Commit the changes and close the connection
cache_conn.commit()
cache_conn.close()

#######################################
#             Cache - END
#######################################
