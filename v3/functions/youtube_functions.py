import re
import requests
import xml.etree.ElementTree as ET
import json
import sys
import sqlite3
import time

CACHE_DB_FILE = "youtube_cache.sqlite"
CACHE_DURATION = 60 * 24 * 60 * 60  # 60 days in seconds


def get_cached_response(request_hash):
    conn = sqlite3.connect(CACHE_DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT response_json, timestamp FROM youtube_cache WHERE request_hash = ?",
        (request_hash,),
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        response_json, timestamp = result
        if time.time() - timestamp < CACHE_DURATION:
            return json.loads(response_json)

    return None


def cache_response(request_hash, response_json):
    conn = sqlite3.connect(CACHE_DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO youtube_cache (request_hash, response_json, timestamp) VALUES (?, ?, ?)",
        (request_hash, json.dumps(response_json), int(time.time())),
    )

    conn.commit()
    conn.close()


def generate_request_hash(base_url, params):
    return base_url + "_" + "_".join(f"{key}={value}" for key, value in params.items())


def get_video_urls_from_channel_list_50(api_key, channel_ids):
    video_urls = []

    for channel_id in channel_ids:
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "type": "video",
            "maxResults": 50,  # Maximum allowed by the API
            "fields": "items/id/videoId",
        }

        request_hash = generate_request_hash(base_url, params)
        cached_response = get_cached_response(request_hash)

        if cached_response:
            response_json = cached_response
        else:
            response = requests.get(base_url, params=params)
            response_json = response.json()
            cache_response(request_hash, response_json)

        for item in response_json["items"]:
            video_url = "https://www.youtube.com/watch?v=" + item["id"]["videoId"]
            video_urls.append(video_url)

    return video_urls


def get_video_urls_from_channel_list_full(api_key, channel_ids):
    video_urls = []

    for channel_id in channel_ids:
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "type": "video",
            "maxResults": 50,  # Maximum allowed by the API
            "fields": "items/id/videoId, nextPageToken",
        }

        next_page_token = None
        while True:
            if next_page_token:
                params["pageToken"] = next_page_token

            request_hash = generate_request_hash(base_url, params)
            cached_response = get_cached_response(request_hash)

            if cached_response:
                response_json = cached_response
            else:
                response = requests.get(base_url, params=params)

                if response.status_code == 403:
                    print("API quota exceeded.")
                    sys.exit()

                response_json = response.json()
                cache_response(request_hash, response_json)

            for item in response_json["items"]:
                video_url = "https://www.youtube.com/watch?v=" + item["id"]["videoId"]
                video_urls.append(video_url)

            next_page_token = response_json.get("nextPageToken")
            if not next_page_token:
                break

    return video_urls


def get_video_urls_from_channel_full(api_key, channel_id):
    video_urls = []

    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "channelId": channel_id,
        "part": "snippet",
        "type": "video",
        "maxResults": 50,  # Maximum allowed by the API
        "fields": "items/id/videoId, nextPageToken",
    }

    next_page_token = None
    while True:
        if next_page_token:
            params["pageToken"] = next_page_token

        request_hash = generate_request_hash(base_url, params)
        cached_response = get_cached_response(request_hash)

        if cached_response:
            response_json = cached_response
        else:
            response = requests.get(base_url, params=params)

            if response.status_code == 403:
                print("API quota exceeded.")
                sys.exit()

            response_json = response.json()
            cache_response(request_hash, response_json)

        for item in response_json["items"]:
            video_url = "https://www.youtube.com/watch?v=" + item["id"]["videoId"]
            video_urls.append(video_url)

        next_page_token = response_json.get("nextPageToken")
        if not next_page_token:
            break

    return video_urls


def get_video_urls_from_channel_list_xml(channel_ids):
    all_video_data = []

    for channel_id in channel_ids:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        request_hash = url
        cached_response = get_cached_response(request_hash)

        if cached_response:
            root = ET.fromstring(cached_response)
        else:
            response = requests.get(url)

            if response.status_code != 200:
                print(
                    f"Error: Unable to fetch data for channel_id {channel_id}. Status code: {response.status_code}"
                )
                continue

            xml_content = response.content
            root = ET.fromstring(xml_content)
            cache_response(request_hash, xml_content.decode('utf-8'))

        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            video_data = {}
            title_element = entry.find("{http://www.w3.org/2005/Atom}title")
            video_data["video_title"] = (
                title_element.text if title_element is not None else None
            )

            published_element = entry.find("{http://www.w3.org/2005/Atom}published")
            video_data["publish_date"] = (
                published_element.text if published_element is not None else None
            )

            author_element = entry.find("{http://www.w3.org/2005/Atom}author")
            if author_element is not None:
                name_element = author_element.find("{http://www.w3.org/2005/Atom}name")
                video_data["channel_title"] = (
                    name_element.text if name_element is not None else None
                )
            else:
                video_data["channel_title"] = None

            video_data["channel_url"] = f"https://www.youtube.com/channel/{channel_id}"
            video_id_element = entry.find(
                "{http://www.youtube.com/xml/schemas/2015}videoId"
            )
            if video_id_element is not None:
                video_data[
                    "video_url"
                ] = f"https://www.youtube.com/watch?v={video_id_element.text}"
            else:
                video_data["video_url"] = None

            media_group = entry.find("{http://search.yahoo.com/mrss/}group")
            if media_group is not None:
                description_element = media_group.find(
                    "{http://search.yahoo.com/mrss/}description"
                )
                video_data["video_description"] = (
                    description_element.text
                    if description_element is not None
                    else None
                )
            else:
                video_data["video_description"] = None

            all_video_data.append(video_data)

    return all_video_data


def get_video_details(api_key, video_url):
    video_id_regex = re.compile(r"v=([^&]+)")
    match = video_id_regex.search(video_url)

    if not match:
        return None

    video_id = match.group(1)

    base_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": api_key,
        "id": video_id,
        "part": "snippet",
        "fields": "items(snippet(title,channelTitle,channelId,publishedAt,description))",
    }

    request_hash = generate_request_hash(base_url, params)
    cached_response = get_cached_response(request_hash)

    if cached_response:
        snippet = cached_response["items"][0]["snippet"]
    else:
        response = requests.get(base_url, params=params)

        if response.status_code == 403:
            print("API quota exceeded.")
            sys.exit()

        response_json = response.json()
        cache_response(request_hash, response_json)
        snippet = response_json["items"][0]["snippet"]

    video_details = {
        "video_name": snippet["title"],
        "channel_name": snippet["channelTitle"],
        "channel_url": f"https://www.youtube.com/channel/{snippet['channelId']}",
        "publish_date": snippet["publishedAt"],
        "video_description": snippet["description"],
    }

    return video_details


def get_channels_by_game(api_key, game_name):
    base_url = "https://www.googleapis.com/youtube/v3/search"
    channels = []
    next_page_token = None

    while True:
        params = {
            "key": api_key,
            "q": game_name,
            "part": "snippet",
            "type": "channel",
            "maxResults": 50,  # Maximum allowed by the API
            "fields": "items(snippet(channelId,channelTitle)), nextPageToken",
            "pageToken": next_page_token,
        }

        request_hash = generate_request_hash(base_url, params)
        cached_response = get_cached_response(request_hash)

        if cached_response:
            response_json = cached_response
        else:
            response = requests.get(base_url, params=params)

            if response.status_code == 403:
                print("API quota exceeded.")
                return channels

            response_json = response.json()
            cache_response(request_hash, response_json)

        for item in response_json["items"]:
            channel_info = {
                "channel_id": item["snippet"]["channelId"],
                "channel_title": item["snippet"]["channelTitle"],
            }
            if channel_info not in channels:
                channels.append(channel_info)

        next_page_token = response_json.get("nextPageToken")
        if not next_page_token:
            break

    return channels

def check_channel_onboarded(channel_id, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute a query to check if the channel ID exists in the table
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM onboarded_channels WHERE id = ?)", (channel_id,)
    )
    result = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    # Return True if the channel ID exists, False otherwise
    return bool(result)


def check_channel_pending(channel_id, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute a query to check if the channel ID exists in the table
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM pending_channels WHERE id = ?)", (channel_id,)
    )
    result = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    # Return True if the channel ID exists, False otherwise
    return bool(result)


def delete_channel_onboarded(channel_id, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Delete the channel from the onboarded_channels table
    cursor.execute("DELETE FROM onboarded_channels WHERE id = ?", (channel_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def delete_channel_pending(channel_id, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Delete the channel from the pending_channels table
    cursor.execute("DELETE FROM pending_channels WHERE id = ?", (channel_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def add_channel_to_onboarded(channel_id, channel_name, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Add the channel to the onboarded_channels table
    cursor.execute(
        "INSERT INTO onboarded_channels (id, name) VALUES (?, ?)",
        (channel_id, channel_name),
    )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def add_channel_to_pending(channel_id, channel_name, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Add the channel to the pending_channels table
    cursor.execute(
        "INSERT INTO pending_channels (id, name) VALUES (?, ?)",
        (channel_id, channel_name),
    )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def get_channel_name_from_onboarded(channel_id, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Retrieve the channel name from the onboarded_channels table
    cursor.execute("SELECT name FROM onboarded_channels WHERE id = ?", (channel_id,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # Return the channel name if found, or None if not found
    return result[0] if result else None


def get_channel_name_from_pending(channel_id, db_file):
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Retrieve the channel name from the pending_channels table
    cursor.execute("SELECT name FROM pending_channels WHERE id = ?", (channel_id,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # Return the channel name if found, or None if not found
    return result[0] if result else None
