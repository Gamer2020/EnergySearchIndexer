import requests
import json
import os
import regex

PTCGL_DECK_PATTERN_1 = regex.compile(
    r"(?s)((?<=\n|^).*\d+.*\n)+",
    flags=regex.IGNORECASE,
)



# Create a new deck
def youtube_create_deck(video_info, video_url, API_URL, API_TOKEN):
    headers = {
        "X-Auth-Token": API_TOKEN,
        "Content-Type": "application/json",
    }

    API_Target = API_URL + "decks/"

    if contains_deck(video_info["video_description"]) == True:
        ptcgl_deck_list_text = get_deck(video_info["video_description"])
        video_info.pop("video_description", None)
        new_deck_data = {
            "deck_name": video_info["video_name"],
            "cards": ptcgl_deck_list_text,
            "visible": "YES",
            "source_type": "YOUTUBE",
            "source_info": video_info,
            "source_identifier": video_url,
            "featuredcard": "base1-58",
            "unlimited_legality": "Legal",
            "standard_legality": "Legal",
            "expanded_legality": "Legal",
        }

        try:
            response = requests.post(
                API_Target, headers=headers, data=json.dumps(new_deck_data), timeout=30
            )
            if response.status_code == 201:
                return response.json()
        except (requests.exceptions.Timeout, requests.exceptions.HTTPError) as err:
            debug_log_message(
                "debug", "response_errors.txt", "Error: " + str(err) + "\n"
            )

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
    return bool(regex.search(PTCGL_DECK_PATTERN_1, deck_string))


def get_deck(deck_string):
    match = regex.search(PTCGL_DECK_PATTERN_1, deck_string)
    if match:
        deck_list = match.group(1)
        deck_list = regex.sub(
            r"^(Pokémon|Trainer|Energy):.*$|Total Cards: 60",
            "",
            deck_list,
            flags=regex.MULTILINE | regex.IGNORECASE,
        )
        # Remove leading characters on each line
        deck_list = regex.sub(r"^\W*\s*", "", deck_list, flags=regex.MULTILINE)
        # Remove extra newlines and spaces
        deck_list = regex.sub(r"\n{2,}", "\n", deck_list)
        deck_list = regex.sub(r"\s{2,}", " ", deck_list)
        return deck_list.strip()
    return None



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
