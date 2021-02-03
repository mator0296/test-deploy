from unittest.mock import patch

import pytest
from bitso.errors import ApiError
from graphql import GraphQLError

from mesada.withdrawal.bitso import make_bitso_spei_withdrawal


@pytest.mark.integration
@patch("mesada.withdrawal.bitso.bitso")
def test_bitso_spei_withdrawal_success(mock_api):
    mock_api.spei_withdrawal.return_value = "Succesfull API call"
    withdrawal = make_bitso_spei_withdrawal(
        "012345678901234567", "Satoshi", "Nakamoto", "1.0"
    )
    assert withdrawal is not None


@pytest.mark.integration
@patch("mesada.withdrawal.bitso.bitso")
def test_bitso_spei_withdrawal_failure(mock_api):

    mock_api.Api.side_effect = ApiError("Test")
    with pytest.raises(GraphQLError):
        make_bitso_spei_withdrawal("012345678901234567", "Satoshi", "Nakamoto", "1.0")
