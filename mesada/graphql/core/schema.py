import urllib

import graphene
import graphql_jwt
from django.contrib.sites.shortcuts import get_current_site

from .mutations import Login


class CoreMutations(graphene.ObjectType):
    token_create = graphql_jwt.ObtainJSONWebToken.Field()
    token_refresh = graphql_jwt.Refresh.Field()
    token_verify = graphql_jwt.Verify.Field()
    login = Login.Field()


class CoreQueries(graphene.ObjectType):
    customer_support_info = graphene.Field(
        graphene.String,
        description="All the information in order to support the customer",
    )

    def resolve_customer_support_info(self, info, **kwargs):
        site = get_current_site(info).settings
        phone_number = urllib.parse.quote_plus(site.whatsapp_phone_number)
        message = urllib.parse.quote_plus(site.whatsapp_message)
        link = (
            "https://api.whatsapp.com/send?phone=" + phone_number + "&text=" + message
        )
        return link
