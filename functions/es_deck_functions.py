import requests
import json
import re
import os

PTCGL_DECK_PATTERN = (
    r'(?s)(Pokémon: \d+.*\n\n(?:Trainer|Trainers): \d+.*\n\n(?:Energy|Energies): \d+.*(?:\n\nTotal Cards: 60)?)'
)


# Create a new deck
def youtube_create_deck(video_info, video_url, API_URL, API_TOKEN):
    headers = {
        "X-Auth-Token": API_TOKEN,
        "Content-Type": "application/json",
    }

    API_Target = API_URL + "decks/"

    if contains_deck(video_info["video_description"]) == True:
        video_info.pop("video_description", None)
        new_deck_data = {
            "deck_name": video_info["video_name"],
            "cards": "card1,card2,card3",
            "visible": "YES",
            "source_type": "YOUTUBE",
            "source_info": video_info,
            "source_identifier": video_url,
            "featuredcard": "Good Card",
            "unlimited_legality": "Legal",
            "standard_legality": "Legal",
            "expanded_legality": "Legal",
        }

        response = requests.post(
            API_Target, headers=headers, data=json.dumps(new_deck_data)
        )
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error: {response.text}")
    else:
        print("No deck list...")
        debug_log_message(
            "debug", "regex_deck_list.txt", "No deck list for : " + video_url + "\n"
        )


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


def contains_deck(deck_string):
    if not deck_string:
        return False
    return bool(re.search(PTCGL_DECK_PATTERN, deck_string))


def get_deck(deck_string):
    match = re.search(PTCGL_DECK_PATTERN, deck_string)
    return match.group(1) if match else None


def debug_log_message(subfolder_name, file_name, text):
    # Create subfolder if it doesn't exist
    if not os.path.exists(subfolder_name):
        os.makedirs(subfolder_name)

    # Create file if it doesn't exist
    file_path = os.path.join(subfolder_name, file_name)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass  # Create an empty file

    # Append text to file
    with open(file_path, "a") as f:
        f.write(text)


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
