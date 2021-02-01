import random
import string

import pytest
from django.contrib.auth.models import Permission  # noqa: E402

from mesada.account.models import User  # noqa: E402

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
