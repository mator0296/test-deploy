from django.db import models


class paymentMethods(models.Model):

    type_method = models.CharField(max_length=50)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    # network
    last_digits = models.CharField(max_length=4)
    # fingerprint
    verification_cvv = models.CharField(max_length=3)
    # verification_avs
    phonenumber = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    country_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
