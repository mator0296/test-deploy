import unittest
import pytest

from unittest.mock import patch
from mesada.withdrawal.bitso import make_bitso_spei_withdrawal
from bitso.errors import ApiError


class TestBitsoIntegration(unittest.TestCase):
    @pytest.mark.integration
    @patch("mesada.withdrawal.bitso.bitso")
    def test_bitso_spei_withdrawal_success(self, mock_api):
        mock_api.spei_withdrawal.return_value = "Succesfull API call"
        withdrawal = make_bitso_spei_withdrawal(
            "012345678901234567", "Satoshi", "Nakamoto", "1.0"
        )
        assert withdrawal is not None

    @pytest.mark.integration
    @patch("mesada.withdrawal.bitso.bitso")
    def test_bitso_spei_withdrawal_failure(self, mock_api):

        mock_api.Api.side_effect = ApiError("Test")
        withdrawal = make_bitso_spei_withdrawal(
            "012345678901234567", "Satoshi", "Nakamoto", "1.0"
        )
        assert withdrawal is None
