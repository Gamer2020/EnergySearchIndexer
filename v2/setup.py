import yaml
import sqlite3
import os

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(current_dir)

# Open the file using the updated path
config_path = os.path.join(current_dir, 'config.yml')
with open(config_path, 'r') as config_file:
    yaml_data = yaml.safe_load(config_file)

# Get the preloaded_channels from the YAML data
preloaded_channels = yaml_data['config']['preloaded_channels']

# Connect to the database (creates a new file if it doesn't exist)
conn = sqlite3.connect('youtube.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS onboarded_channels (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )''')

# Insert or update preloaded_channels in the database
for channel in preloaded_channels:
    channel_id = channel.split()[0].strip('"')
    channel_name = channel.split()[1].strip('#@')
    cursor.execute("INSERT OR REPLACE INTO onboarded_channels (id, name) VALUES (?, ?)", (channel_id, channel_name))

# Commit the changes and close the connection
conn.commit()
conn.close()
