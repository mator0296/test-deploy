import requests
from django.conf import settings

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {123456789}",
}


def get_amount(body: dict) -> dict:
    """
    Function to get the amount from galactus
    """
    url = f"{settings.GALACTUS_URL}/get_amount"
    try:
        response = requests.request("GET", url, headers=HEADERS, json=body)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise GraphQLError("Internal Server Error: %s" % err.response.json()["message"])

    return response.json()
