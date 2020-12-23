"""
Circle communications lay in this file.

For more information on the Circle Payments API check out:
https://developers.circle.com/docs/getting-started-with-the-circle-payments-api
"""

import environ
import requests

env = environ.Env()
env.read_env(env.str("ENV_PATH", ".env"))

CIRCLE_API_KEY = env("CIRCLE_API_KEY")
CIRCLE_BASE_URL = env("CIRCLE_BASE_URL")


def create_card(body):
    """Save a card within the Circle API."""
    url = f"{CIRCLE_BASE_URL}/cards"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, json=body)

    print(response.text)
