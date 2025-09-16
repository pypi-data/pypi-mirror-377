import requests

URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


def make_request(label, word):
    if word.strip():
        url = URL + word
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()[0]
        elif response.status_code == 404:
            label.config(text="Word not found.")
            return None
        else:
            label.config(text=f"Error {response.status_code}")
            return None
    return None


def get_definition(label, word):
    request = make_request(label, word)
    if request:
        label.config(
            text=f"{word}, {request["meanings"][0]["partOfSpeech"]}: {request["meanings"][0]["definitions"][0]["definition"]}"
        )
    label.grid(row=1, column=0, padx=10, pady=5)


def get_synonyms(label, word):
    request = make_request(label, word)
    if request:
        all_synonyms = []  # store the synonyms here because the API is weird :(

        for meaning in request["meanings"]:
            all_synonyms.extend(meaning.get("synonyms", []))

            for definition in meaning["definitions"]:
                all_synonyms.extend(definition.get("synonyms", []))

        # remove any duplicates
        all_synonyms = list(set(all_synonyms))

        if all_synonyms:
            label_text = f"Synonyms for {word} are:\n* " + all_synonyms[0]
            for synonym in all_synonyms[1:]:
                label_text += "\n* " + synonym
        else:
            label_text = "No synonyms found."

        label.config(text=label_text)
    label.grid(row=2, column=0, padx=10, pady=5)


def get_antonyms(label, word):
    request = make_request(label, word)
    if request:
        all_antonyms = []

        for meaning in request["meanings"]:
            all_antonyms.extend(meaning.get("antonyms", []))

            for definition in meaning["definitions"]:
                all_antonyms.extend(definition.get("antonyms", []))

        # remove duplicates
        all_antonyms = list(set(all_antonyms))

        if all_antonyms:
            label_text = f"Antonyms for {word} are:\n* " + all_antonyms[0]
            for antonym in all_antonyms[1:]:
                label_text += "\n* " + antonym
        else:
            label_text = "No antonyms found."
        label.config(text=label_text)
    label.grid(row=2, column=0, padx=10, pady=5)
