from django.contrib.auth.base_user import AbstractBaseUser

from . import CustomerEvents
from .models import CustomerEvent

UserType = AbstractBaseUser


def customer_account_created_event(*, user: UserType) -> CustomerEvent:
    return CustomerEvent.objects.create(user=user, type=CustomerEvents.ACCOUNT_CREATED)
