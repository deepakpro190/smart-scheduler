import requests
import json
import re
from config import MISTRAL_API_KEY, MISTRAL_API_URL

def extract_first_json(text):
    try:
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        return None

def call_mistral(messages):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-tiny",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
        "tool_choice": "none"
    }
    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("\U0001F534 Mistral API Error:", response.status_code, response.text)
        raise Exception(f"{response.status_code} {response.reason}")

    return response.json()["choices"][0]["message"]["content"]

