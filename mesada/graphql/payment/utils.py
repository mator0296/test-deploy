import hashlib


def hash_session_id(session_id):
    return hashlib.md5(session_id.encode("utf-8")).hexdigest()


def get_default_billing_details(user):
    return {
        "name": f"{user.default_address.first_name} {user.default_address.last_name}",
        "city": user.default_address.city,
        "country": str(user.default_address.country),
        "line1": user.default_address.street_address_1,
        "line2": user.default_address.street_address_2,
        "district": user.default_address.country_area,
        "postalCode": user.default_address.postal_code,
    }
