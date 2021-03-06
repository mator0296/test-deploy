import graphene
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy


def clean_seo_fields(data):
    """Extract and assign seo fields to given dictionary."""
    seo_fields = data.pop("seo", None)
    if seo_fields:
        data["seo_title"] = seo_fields.get("title")
        data["seo_description"] = seo_fields.get("description")


def snake_to_camel_case(name):
    """Convert snake_case variable name to camelCase."""
    if isinstance(name, str):
        split_name = name.split("_")
        return split_name[0] + "".join(map(str.capitalize, split_name[1:]))
    return name


def str_to_enum(name):
    """Create an enum value from a string."""
    return name.replace(" ", "_").replace("-", "_").upper()


def from_global_id_strict_type(info, global_id, only_type, field="id"):
    """Resolve a node global id with a strict given type required."""
    if not global_id:
        raise ValidationError({field: "Couldn't resolve to a node: %s" % global_id})
    _type, _id = graphene.Node.from_global_id(global_id)
    graphene_type = info.schema.get_type(_type).graphene_type
    if graphene_type != only_type:
        raise ValidationError({field: "Couldn't resolve to a node: %s" % global_id})
    return _id


def get_user_instance(info):
    AUTHENTICATION_ERROR = pgettext_lazy("Account Error", "You must be logged in")
    if info.context.user.is_authenticated:
        return info.context.user
    raise ValidationError({"authentication": AUTHENTICATION_ERROR})
