from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

MODELS_PERMISSIONS = ["account.manage_staff", "account.manage_users"]


def split_permission_codename(permissions):
    return [permission.split(".")[1] for permission in permissions]


def create_permissions_for_model(model, codename, name):
    content_type = ContentType.objects.get_for_model(model)
    permission, created = Permission.objects.get_or_create(
        codename=codename, name=name, content_type=content_type
    )


def get_permissions(permissions=None):
    if permissions is None:
        permissions = MODELS_PERMISSIONS

    codenames = split_permission_codename(permissions)
    return (
        Permission.objects.filter(codename__in=codenames)
        .prefetch_related("content_type")
        .order_by("codename")
    )
