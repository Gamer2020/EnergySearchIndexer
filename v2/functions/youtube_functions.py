import re
import requests
import xml.etree.ElementTree as ET
import json
import sys


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

        response = requests.get(base_url, params=params)
        response_json = response.json()
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

            response = requests.get(base_url, params=params)

            # Check if we've hit the quota
            if response.status_code == 403:
                print("API quota exceeded.")
                sys.exit()

            response_json = response.json()

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
        response = requests.get(url)

        if response.status_code != 200:
            print(
                f"Error: Unable to fetch data for channel_id {channel_id}. Status code: {response.status_code}"
            )
            continue

        xml_content = response.content
        root = ET.fromstring(xml_content)

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

    response = requests.get(base_url, params=params)

    # Check if we've hit the quota
    if response.status_code == 403:
        print("API quota exceeded.")
        sys.exit()

    response_json = response.json()

    if not response_json["items"]:
        return None

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

        response = requests.get(base_url, params=params)

        # Check if we've hit the quota
        if response.status_code == 403:
            print("API quota exceeded.")
            sys.exit()

        response_json = response.json()

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
