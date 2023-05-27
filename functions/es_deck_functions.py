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

        decks = extract_decks(ptcgl_deck_list_text)

        for i, deck in enumerate(decks):
            # print(f"Deck {i+1}:\n{deck}")

            if i > 0:
                new_deck_data = {
                    "deck_name": video_info["video_name"],
                    "cards": deck,
                    "visible": "YES",
                    "source_type": "YOUTUBE",
                    "source_info": video_info,
                    "source_identifier": video_url + "&deck=" + str(i + 1),
                    "featuredcard": "base1-58",
                    "format_legality": "standard",
                }
            else:
                new_deck_data = {
                    "deck_name": video_info["video_name"],
                    "cards": deck,
                    "visible": "YES",
                    "source_type": "YOUTUBE",
                    "source_info": video_info,
                    "source_identifier": video_url,
                    "featuredcard": "base1-58",
                    "format_legality": "standard",
                }

            try:
                response = requests.post(
                    API_Target,
                    headers=headers,
                    data=json.dumps(new_deck_data),
                    timeout=120,
                )
                # if response.status_code == 201:
                #     return response.json()
            except (requests.exceptions.Timeout, requests.exceptions.HTTPError) as err:
                debug_log_message(
                    "debug", "response_errors.txt", "Error: " + str(err) + "\n"
                )

    else:
        # print("No deck list...")
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


def extract_decks(text):
    lines = text.split("\n")
    card_lines = [line for line in lines if line.split(" ", 1)[0].isdigit()]
    decks = []
    current_deck = []
    current_sum = 0
    for line in card_lines:
        quantity = int(line.split(" ", 1)[0])
        current_deck.append(line)
        current_sum += quantity
        if current_sum == 60:
            decks.append("\n".join(current_deck))
            current_deck = []
            current_sum = 0
    if current_deck:  # handle any remaining cards
        decks.append("\n".join(current_deck))
    return decks


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
