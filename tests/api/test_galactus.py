from unittest.mock import Mock, patch

import pytest
from django.conf import settings

from mesada.checkout import get_amount, HEADERS

@pytest.mark.integration
@patch("mesada.checkout.utils.requests")
def test_get_amount(mock_requests, user_api_client):
    body = {
        "amount_to_convert": "50.32",
        "block_amount": True,
        "checkout_token": "token123"
    }
    get_amount(body)
    url = f"{settings.GALACTUS_URL}/get_amount"
    mock_requests.request.assert_called_once_with("GET", url, headers=HEADERS, json=body)