from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Address, User


class UserForm(ModelForm):
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if not first_name or not last_name:
            raise ValidationError("Must provide first and last name")

    class Meta:
        model = User
        exclude = [
            "is_staff",
            "is_active",
            "note",
            "date_joined",
            "utm_tracking",
            "email",
            "password",
        ]


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ["is_visible"]
