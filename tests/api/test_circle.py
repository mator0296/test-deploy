from unittest.mock import patch

import pytest
from django.conf import settings

from mesada.payment.circle import HEADERS


@pytest.mark.integration
@patch("mesada.payment.circle.requests")
def test_create_public_key(mock_requests, user_api_client):
    query = """
    mutation createPublicKey{
        createPublicKey{
            keyId
            publicKey
            errors{
            field
            message
            }
        }
    }
    """
    variables_values = {}
    user_api_client.post_graphql(query, variables_values)

    url = f"{settings.CIRCLE_BASE_URL}/encryption/public"
    mock_requests.request.assert_called_once_with("GET", url, headers=HEADERS)
