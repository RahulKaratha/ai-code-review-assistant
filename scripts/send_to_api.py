import os

import requests
from scripts.build_payload import build_payload


API_URL = os.getenv(
    "AI_REVIEW_API_URL",
    "http://127.0.0.1:8000/analyze"
)


def send_review_request():

    payload = build_payload()

    response = requests.post(
        API_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":

    result = send_review_request()

    print("\n===== AI CODE REVIEW =====\n")

    print(result)