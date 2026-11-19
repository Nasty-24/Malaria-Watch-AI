# Coarse bounding boxes (lat_min, lat_max, lon_min, lon_max), with a small margin.
# They overlap neighbouring countries and each other. A true boundary check arrives
# with the PostGIS step; until then this only blocks clearly unsupported locations.
BOUNDS = {
    # lat_max covers Turkana's northern edge (the Ilemi Triangle, ~5.43 N in geoBoundaries).
    "KEN": (-4.9, 5.6, 33.8, 42.0),
    "TZA": (-11.8, -0.9, 29.2, 40.6),
    "ETH": (3.3, 15.0, 32.9, 48.1),
}


def inside_supported_area(latitude, longitude, country=None):
    codes = [country] if country else list(BOUNDS)
    for code in codes:
        lat_min, lat_max, lon_min, lon_max = BOUNDS[code]
        if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
            return True
    return False