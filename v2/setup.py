import yaml
import sqlite3
import os

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(current_dir)

# Open the file using the updated path
config_path = os.path.join(current_dir, "config.yml")
print("Config path:", config_path)

with open(config_path, "r") as config_file:
    yaml_data = yaml.safe_load(config_file)

# Get the preloaded_channels from the YAML data
preloaded_channels = yaml_data["config"]["preloaded_channels"]
print("Preloaded channels:", preloaded_channels)

# Connect to the database (creates a new file if it doesn't exist)
conn = sqlite3.connect("youtube.sqlite")
print("Connected to database")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute(
    """CREATE TABLE IF NOT EXISTS onboarded_channels (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )"""
)
print("Table created")

# Insert or update preloaded_channels in the database
for channel in preloaded_channels:
    channel_parts = channel.split("|")
    if len(channel_parts) >= 2:
        channel_id = channel_parts[0].strip()
        channel_name = channel_parts[1].strip()
        print("Inserting channel:", channel_id, channel_name)
        cursor.execute(
            "INSERT OR REPLACE INTO onboarded_channels (id, name) VALUES (?, ?)",
            (channel_id, channel_name),
        )

# Commit the changes and close the connection
conn.commit()
conn.close()
print("Database updated successfully")
