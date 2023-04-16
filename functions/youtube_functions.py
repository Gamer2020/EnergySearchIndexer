import re
import requests


def get_video_urls_from_channel_list(api_key, channel_ids):
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
            response_json = response.json()

            for item in response_json["items"]:
                video_url = "https://www.youtube.com/watch?v=" + item["id"]["videoId"]
                video_urls.append(video_url)

            next_page_token = response_json.get("nextPageToken")
            if not next_page_token:
                break

    return video_urls


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
