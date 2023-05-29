import sqlite3
import os

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(current_dir)

# Create the SQLite database file path using the current directory
db_file_path = os.path.join(current_dir, 'youtube.sqlite')

# Connect to the database
conn = sqlite3.connect(db_file_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Query all entries from the onboarded_channels table
cursor.execute("SELECT * FROM onboarded_channels")
result = cursor.fetchall()

# Loop through the entries and print the data
for row in result:
    channel_id = row[0]
    channel_name = row[1]
    print(f"Channel ID: {channel_id}, Channel Name: {channel_name}")

# Close the cursor and the connection
cursor.close()
conn.close()
