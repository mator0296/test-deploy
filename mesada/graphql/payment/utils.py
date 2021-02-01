import base64
import hashlib
import json

import pgpy

from mesada.payment.circle import request_encryption_key


def hash_session_id(session_id):
    return hashlib.md5(session_id.encode("utf-8")).hexdigest()


def get_default_billing_details(user):
    if not user.default_address.first_name or not user.default_address.last_name:
        name = f"{user.first_name} {user.last_name}"
    else:
        name = f"{user.default_address.first_name} {user.default_address.last_name}"

    return {
        "name": name,
        "city": user.default_address.city,
        "country": str(user.default_address.country),
        "line1": user.default_address.street_address_1,
        "line2": user.default_address.street_address_2,
        "district": user.default_address.country_area,
        "postalCode": user.default_address.postal_code,
    }


def generate_dummy_encrypted_data():
    key_id, public_key = request_encryption_key()
    dummy_message = {"number": "4007400000000007", "cvv": "123"}

    key, _ = pgpy.PGPKey.from_blob(base64.b64decode(public_key))
    message = pgpy.PGPMessage.new(json.dumps(dummy_message))
    ciphertext = key.pubkey.encrypt(message)

    encrypted_message = base64.b64encode(bytes(ciphertext))

    return key_id, encrypted_message.decode()
