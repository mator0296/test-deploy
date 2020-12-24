"""
Circle communications lay in this file.

For more information on the Circle Payments API check out:
https://developers.circle.com/docs/getting-started-with-the-circle-payments-api
"""

from django.conf import settings
import requests

CIRCLE_API_KEY = settings.CIRCLE_API_KEY
CIRCLE_BASE_URL = settings.CIRCLE_BASE_URL


def create_card(body):
    """Save a card within the Circle API.

    Args:
        body (dict): Request body.
    """
    url = f"{CIRCLE_BASE_URL}/cards"
    print(url)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, json=body)

    return response
