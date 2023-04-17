import requests
import json


# Create a new deck
def youtube_create_deck(video_info, video_url, API_URL, API_TOKEN):
    headers = {
        "X-Auth-Token": API_TOKEN,
        "Content-Type": "application/json",
    }

    API_Target = API_URL + "decks/"

    video_info.pop("video_description", None)
    new_deck_data = {
        "deck_name": video_info["video_name"],
        "cards": "card1,card2,card3",
        "visible": "YES",
        "source_type": "YOUTUBE",
        "source_info": video_info,
        "source_identifier": video_url,
    }

    response = requests.post(
        API_Target, headers=headers, data=json.dumps(new_deck_data)
    )
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Error: {response.text}")


# Check If Deck Exits
def youtube_check_deck_exists(deck_id, API_URL, API_TOKEN):
    headers = {
        "X-Auth-Token": API_TOKEN,
        "Content-Type": "application/json",
    }

    API_Target = API_URL + "decks/"

    response = requests.get(API_Target, headers=headers, params={"id": deck_id})
    if response.status_code == 200:
        return True
    else:
        return False


# Get a deck by id
# def youtube_get_deck(deck_id, API_URL, API_TOKEN):
#     headers = {
#         "Authorization": f"Bearer {API_TOKEN}",
#         "Content-Type": "application/json",
#     }
#     response = requests.get(API_URL, headers=headers, params={"id": deck_id})
#     if response.status_code == 200:
#         return response.json()
#     else:
#         raise Exception(f"Error: {response.text}")
