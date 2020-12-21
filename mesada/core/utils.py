def get_client_ip(request):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
        return ip.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", None)


def get_country_by_ip(ip_address):
    # geo_data = georeader.get(ip_address)
    # if geo_data and "country" in geo_data and "iso_code" in geo_data["country"]:
    #     country_iso_code = geo_data["country"]["iso_code"]
    #     if country_iso_code in countries:
    #         return Country(country_iso_code)
    return None
