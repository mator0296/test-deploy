import random
import string

import pytest
from django.contrib.auth.models import Permission  # noqa: E402

from mesada.account.models import Recipient, User  # noqa: E402
from mesada.checkout.models import Checkout  # noqa: E402
from mesada.payment import PaymentMethodTypes  # noqa: E402
from mesada.payment.models import PaymentMethods  # noqa: E402

pytestmark = pytest.mark.django_db


def random_string(n):
    return "".join(random.choice(string.ascii_lowercase) for _ in range(n))


def random_numbers(n):
    """Return random string of numbers"""
    return "".join(random.choice(string.digits) for _ in range(n))


@pytest.fixture(autouse=True)
def setup_db(db):
    return db


@pytest.fixture()
def staff_user():
    """Return a staff member."""
    return User.objects.create_user(
        email="staff_" + random_string(6) + "@example.com",
        password="password",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def user():
    mail = random_string(6) + "@mail.com"
    user = User.objects.create_user(mail, "password")
    return user


@pytest.fixture
def permission_manage_users():
    return Permission.objects.get(codename="manage_users")


@pytest.fixture
def payment_method_ach():
    return PaymentMethods.objects.create(
        type=PaymentMethodTypes.ACH, email="test_payment_method@example.com"
    )


@pytest.fixture
def recipient(user):
    return Recipient.objects.create(
        first_name="Alexander",
        last_name="Romero",
        alias="alesande",
        email="alexander_romero_test@example.com",
        clabe="123456789123456789",
        user=user,
    )


@pytest.fixture
def checkout(user):
    checkout_payment_method = PaymentMethods.objects.create(
        type=PaymentMethodTypes.CARD, email="test_payment_method2@example.com"
    )
    checkout_recipient = Recipient.objects.create(
        first_name="Daniel",
        last_name="Varela",
        alias="dvd6412",
        email="daniel_varela_test@example.com",
        clabe="987654321987654321",
        user=user,
    )
    return Checkout.objects.create(
        amount="220.0",
        fees="1.25",
        total_amount="221.25",
        recipient_amount="45.50",
        recipient=checkout_recipient,
        payment_method=checkout_payment_method,
        user=user,
    )
