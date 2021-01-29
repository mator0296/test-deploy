import json

from django.core.serializers.json import DjangoJSONEncoder
from djmoney.money import Money

from .conftest import random_numbers, random_string

from mesada.account.models import Recipient
from mesada.checkout import CheckoutStatus
from mesada.checkout.models import Checkout
from mesada.graphql.core.utils import snake_to_camel_case
from mesada.payment import PaymentStatus
from mesada.payment.models import Payment


def _get_graphql_content_from_response(response):
    return json.loads(response.content.decode("utf8"))


def get_graphql_content(response):
    """Get's GraphQL content from the response, and optionally checks if it
    contains any operating-related errors, eg. schema errors or lack of
    permissions.
    """
    content = _get_graphql_content_from_response(response)
    assert "errors" not in content, content["errors"]
    return content


def assert_no_permission(response):
    content = _get_graphql_content_from_response(response)
    assert "errors" in content, content
    assert content["errors"][0]["message"] == (
        "You do not have permission to perform this action"
    ), content["errors"]


def get_multipart_request_body(query, variables, file, file_name):
    """Create request body for multipart GraphQL requests.

    Multipart requests are different than standard GraphQL requests, because
    of additional 'operations' and 'map' keys.
    """
    return {
        "operations": json.dumps(
            {"query": query, "variables": variables}, cls=DjangoJSONEncoder
        ),
        "map": json.dumps({file_name: ["variables.file"]}, cls=DjangoJSONEncoder),
        file_name: file,
    }


def convert_dict_keys_to_camel_case(d):
    """Changes dict fields from d[field_name] to d[fieldName].

    Useful when dealing with dict data such as address that need to be parsed
    into graphql input.
    """
    data = {}
    for k, v in d.items():
        new_key = snake_to_camel_case(k)
        data[new_key] = d[k]
    return data


http_error_test_data = [(400, "Bad Request"), (401, "Unauthorized")]


def recipient(user) -> Recipient:
    recipient = Recipient.objects.create(
        first_name="Test",
        last_name="Recipient",
        user=user,
        email=random_string(6) + "@mail.com",
        alias="Recipient alias",
        clabe=random_numbers(18),
        bank="Bancomer",
    )

    return recipient


def checkout(user, recipient: Recipient) -> Checkout:
    checkout = Checkout.objects.create(
        checkout_token=f"{random_string(4)}-{random_numbers(6)}-{random_string(4)}",
        user=user,
        recipient=recipient,
        status=CheckoutStatus.PENDING,
        active=True,
        amount=Money(10.0, "USD"),
        total_amount=Money(10.0, "USD"),
        fees=Money(2.0, "USD"),
        recipient_amount=Money(200.0, "MXN"),
    )

    return checkout


def payment(user) -> Payment:
    payment = Payment.objects.create(
        status=PaymentStatus.CONFIRMED,
        type="payment",
        merchant_id=random_numbers(6),
        merchant_wallet_id=random_numbers(12),
        amount=Money(10.0, "USD"),
        source={},
        metadata={},
        user=user,
    )

    return payment
