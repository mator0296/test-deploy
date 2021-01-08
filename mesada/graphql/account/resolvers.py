import graphene_django_optimizer as gql_optimizer
from django.db.models import Q
from django.utils.translation import pgettext_lazy

from ...account import models
from ...core.utils import get_client_ip, get_country_by_ip
from ..utils import filter_by_query_param
from .types import AddressValidationData

USER_SEARCH_FIELDS = (
    "email",
    "first_name",
    "last_name",
    "default_address__first_name",
    "default_address__last_name",
    "default_address__city",
    "default_address__country",
)


RECIPIENT_SEARCH_FIELDS = ("alias", "email", "first_name", "last_name")

ADDRESS_SEARCH_FIELDS = ("address_name", "postal_code")



def resolve_customers(info, query):
    qs = models.User.objects.filter(Q(is_staff=False))
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=USER_SEARCH_FIELDS
    )
    qs = qs.order_by("email")
    qs = qs.distinct()
    return gql_optimizer.query(qs, info)


def resolve_staff_users(info, query):
    qs = models.User.objects.filter(is_staff=True)
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=USER_SEARCH_FIELDS
    )
    qs = qs.order_by("email")
    qs = qs.distinct()
    return gql_optimizer.query(qs, info)


def resolve_address_validator(info, country_code, country_area, city_area):
    if not country_code:
        client_ip = get_client_ip(info.context)
        country = get_country_by_ip(client_ip)
        if country:
            country_code = country.code
        else:
            return None
    params = {
        "country_code": country_code,
        "country_area": country_area,
        "city_area": city_area,
    }
    rules = {}
    return AddressValidationData(
        country_code=rules.country_code,
        country_name=rules.country_name,
        address_format=rules.address_format,
        address_latin_format=rules.address_latin_format,
        allowed_fields=rules.allowed_fields,
        required_fields=rules.required_fields,
        upper_fields=rules.upper_fields,
        country_area_type=rules.country_area_type,
        # country_area_choices=[
        #     ChoiceValue(area[0], area[1]) for area in rules.country_area_choices
        # ],
        city_type=rules.city_type,
        # city_choices=[ChoiceValue(area[0], area[1]) for area in rules.city_choices],
        city_area_type=rules.city_type,
        # city_area_choices=[
        #     ChoiceValue(area[0], area[1]) for area in rules.city_area_choices
        # ],
        postal_code_type=rules.postal_code_type,
        postal_code_matchers=[
            compiled.pattern for compiled in rules.postal_code_matchers
        ],
        postal_code_examples=rules.postal_code_examples,
        postal_code_prefix=rules.postal_code_prefix,
    )


def resolve_recipient_(info, id):
    qs = models.Recipient.objects.get(pk=id)
    return qs


def resolve_recipients_(info, search, query):
    qs = models.Recipient.objects.filter(
        Q(alias__icontains=search)
        | Q(email__icontains=search)
        | Q(first_name__icontains=search)
    )
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=RECIPIENT_SEARCH_FIELDS
    )
    return qs

def resolve_address(info, id):
    return models.Address.objects.get(pk=id)


def resolve_addresses(info, search, query):
    qs = models.Address.objects.filter(Q(address_name=search) | Q(postal_code=search))
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=ADDRESS_SEARCH_FIELDS
    )
    qs = qs.distinct()
    return gql_optimizer.query(qs, info)
