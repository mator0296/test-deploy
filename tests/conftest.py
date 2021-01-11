import random
import string
import django
django.setup()  # noqa: E731
from django.contrib.auth.models import Permission  # noqa: E402

from mesada.account.models import User  # noqa: E402

pytestmark = pytest.mark.django_db


def random_string(n):
    return "".join(random.choice(string.ascii_lowercase) for _ in range(n))


def random_numbers(n):
    """Return random string of numbers"""
    return "".join(random.choice(string.digits) for _ in range(n))


@pytest.fixture
def settings():
    from django.conf import settings

    return settings


@pytest.fixture()
def staff_user():
    """Return a staff member."""
    staff = User.objects.filter(email="staff_test@example.com")
    staff.delete()
    return User.objects.create_user(
        email="staff_" + random_string(6) + "@example.com",
        password="password",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def customer_user():
    mail = random_string(6) + "@mail.com"
    user = User.objects.filter(email="test@example.com")
    user.delete()
    user = User.objects.create_user(mail, "password")
    return user


@pytest.fixture
def permission_manage_users():
    return Permission.objects.get(codename="manage_users")
