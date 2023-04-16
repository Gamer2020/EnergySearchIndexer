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
