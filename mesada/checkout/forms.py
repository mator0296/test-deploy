from django.forms import ModelForm

from .models import Checkout


class CheckoutForm(ModelForm):
    def save(self, money_fields, user=None):
        if user is not None:
            self.instance.user = user
        self.instance.save()
        return self.instance

    class Meta:
        model = Checkout
        fields = [
            "amount",
            "fees",
            "total_amount",
            "recipient_amount",
            "recipient",
            "payment_method",
            "status",
            "active",
        ]
