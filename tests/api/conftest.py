import json
from unittest import mock

import graphene
import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import reverse
from django.test.client import MULTIPART_CONTENT, Client
from graphql_jwt.shortcuts import get_token
from requests.exceptions import HTTPError

from ..utils import assert_no_permission

from mesada.account.models import User
from mesada.order import OrderStatus
from mesada.order.models import Order

from djmoney.money import Money

from .conftest import random_numbers, random_string

from mesada.account.models import Recipient
from mesada.checkout import CheckoutStatus
from mesada.checkout.models import Checkout
from mesada.payment import PaymentStatus
from mesada.payment.models import Payment

API_PATH = reverse("api")


class ApiClient(Client):
    """GraphQL API client."""

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        self.user = user
        if not user.is_anonymous:
            self.token = get_token(user)
        super().__init__(*args, **kwargs)

    def _base_environ(self, **request):
        environ = super()._base_environ(**request)
        if not self.user.is_anonymous:
            environ.update({"HTTP_AUTHORIZATION": "JWT %s" % self.token})
        return environ

    def post(self, data=None, **kwargs):
        """Send a POST request.

        This wrapper sets the `application/json` content type which is
        more suitable for standard GraphQL requests and doesn't mismatch with
        handling multipart requests in Graphene.
        """
        if data:
            data = json.dumps(data, cls=DjangoJSONEncoder)
        kwargs["content_type"] = "application/json"
        return super().post(API_PATH, data, **kwargs)

    def post_graphql(
        self,
        query,
        variables=None,
        permissions=None,
        check_no_permissions=True,
        **kwargs
    ):
        """Dedicated helper for posting GraphQL queries.

        Sets the `application/json` content type and json.dumps the variables
        if present.
        """
        data = {"query": query}
        if variables is not None:
            data["variables"] = variables
        if data:
            data = json.dumps(data, cls=DjangoJSONEncoder)
        kwargs["content_type"] = "application/json"

        if permissions:
            if check_no_permissions:
                response = super().post(API_PATH, data, **kwargs)
                assert_no_permission(response)
            self.user.user_permissions.add(*permissions)
        return super().post(API_PATH, data, **kwargs)

    def post_multipart(self, *args, permissions=None, **kwargs):
        """Send a multipart POST request.

        This is used to send multipart requests to GraphQL API when e.g.
        uploading files.
        """
        kwargs["content_type"] = MULTIPART_CONTENT

        if permissions:
            response = super().post(API_PATH, *args, **kwargs)
            assert_no_permission(response)
            self.user.user_permissions.add(*permissions)
        return super().post(API_PATH, *args, **kwargs)


@pytest.fixture
def staff_api_client(staff_user):
    return ApiClient(user=staff_user)


@pytest.fixture
def user_api_client(customer_user):
    return ApiClient(user=customer_user)


@pytest.fixture
def api_client():
    return ApiClient(user=AnonymousUser())


@pytest.fixture
def schema_context():
    params = {"user": AnonymousUser()}
    return graphene.types.Context(**params)


@pytest.fixture
def superuser():
    superuser = User.objects.create_superuser("superuser@example.com", "pass")
    return superuser


@pytest.fixture
def user_list_not_active(user_list):
    users = User.objects.filter(pk__in=[user.pk for user in user_list])
    users.update(is_active=False)
    return users


@pytest.fixture
def http_exception(code: int, message: str) -> mock.Mock:
    mock_response = mock.Mock()
    mock_response.json.return_value = {"message": message}
    mock_response.status_code = code

    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)

    return mock_response


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



@pytest.fixture
def order(customer_user):
    recipient = Recipient(customer_user)
    checkout = Checkout(customer_user, recipient)
    payment = Payment(customer_user)

    order = Order.objects.create(
        checkout=checkout,
        payment=payment,
        status=OrderStatus.PENDING,
        user=customer_user,
        recipient=recipient,
        amount=checkout.amount,
        fees=checkout.fees,
        total_amount=checkout.total_amount,
        recipient_amount=checkout.recipient_amount,
    )

    return order
