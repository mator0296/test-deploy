from django.db.models.enums import TextChoices


class Banks(TextChoices):
    BBVA = "bbva"
    BANAMEX = "banamex"
    BANORTE = "banorte"
    SANTANDER = "santander"
