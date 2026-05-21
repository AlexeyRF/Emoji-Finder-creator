import requests
import json
import os

def fetch_emojis():
    # Fetching a comprehensive list of emojis from a reliable source
    # We'll use the unicode-emoji-json project as a base
    url = "https://raw.githubusercontent.com/muan/unicode-emoji-json/main/data-by-emoji.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Transform data to a simpler format if needed
        # For now, we'll keep the emoji as key and its info as value
        with open("emoji_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully fetched {len(data)} emojis.")
    else:
        print("Failed to fetch emoji data.")

if __name__ == "__main__":
    fetch_emojis()
