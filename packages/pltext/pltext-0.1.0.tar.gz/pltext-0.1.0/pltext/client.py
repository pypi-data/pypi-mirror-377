import os
import requests
from dotenv import load_dotenv

# Load env if available
load_dotenv()

class Pltext:
    def __init__(self, api_key: str = None, api_url: str = None):
        # Prefer argument > env var > default
        self.api_key = api_key or os.getenv("PLTEXT_API_KEY")
        self.api_url = api_url or os.getenv("PLTEXT_API_URL", "http://localhost:5033/api/v1/check")

        if not self.api_key:
            raise ValueError("API key missing. Pass Pltext(api_key=...) or set PLTEXT_API_KEY in .env")

    def check_content(self, content: str):
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {"content": content}

        resp = requests.post(self.api_url, json=data, headers=headers)

        if resp.status_code != 200:
            raise Exception(f"API Error {resp.status_code}: {resp.text}")

        return resp.json()