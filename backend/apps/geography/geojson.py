import json

from django.contrib.gis.geos import MultiPolygon
from django.db.models import Func, TextField


def _signed_area(ring):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:])) / 2


def _orient(rings):
    """RFC 7946 right-hand rule: exterior ring counter-clockwise, holes clockwise."""
    oriented = []
    for index, ring in enumerate(rings):
        counter_clockwise = _signed_area(ring) > 0
        if counter_clockwise == (index == 0):
            oriented.append(ring)
        else:
            oriented.append(list(reversed(ring)))
    return oriented


# Display geometry for map layers: ~500 m simplification keeps district shapes recognisable
# while cutting payloads roughly tenfold; 5 decimal places is ~1 m. Region detail keeps the
# stored full-resolution boundary.
DISPLAY_TOLERANCE_DEG = 0.005
DISPLAY_DECIMALS = 5


class DisplayGeoJSON(Func):
    """Database-side display geometry: the same simplification, RFC 7946 orientation and
    rounding as to_geojson_geometry(simplify=True), done in PostGIS so the full-resolution
    boundary never leaves the database. NULL when there is no boundary."""

    template = (
        # ST_Multi keeps the stored MultiPolygon type (simplify demotes one-part shapes).
        "ST_AsGeoJSON(ST_Multi(ST_ForcePolygonCCW(ST_SimplifyPreserveTopology(%(expressions)s, "
        f"{DISPLAY_TOLERANCE_DEG}))), {DISPLAY_DECIMALS})"
    )
    output_field = TextField()


def display_geometry(geojson_text, fallback=None):
    """Parse a DisplayGeoJSON value; use the Python path if PostGIS returned nothing usable."""
    if geojson_text:
        data = json.loads(geojson_text)
        data.pop("crs", None)
        if data.get("type") in ("Polygon", "MultiPolygon") and data.get("coordinates"):
            return data
    return to_geojson_geometry(fallback() if callable(fallback) else fallback, simplify=True)


def _round(rings, decimals):
    return [[[round(x, decimals), round(y, decimals)] for x, y, *_ in ring] for ring in rings]


def to_geojson_geometry(geom, simplify=False):
    """GeoJSON geometry (EPSG:4326, longitude then latitude) or None.

    simplify=True returns a lighter display geometry (topology-preserving, rounded
    coordinates); it falls back to the stored geometry if simplification empties it.
    """
    if geom is None:
        return None
    if simplify:
        simple = geom.simplify(DISPLAY_TOLERANCE_DEG, preserve_topology=True)
        if simple.geom_type == "Polygon" and geom.geom_type == "MultiPolygon":
            simple = MultiPolygon(simple, srid=geom.srid)  # keep the stored geometry type
        if not simple.empty and simple.geom_type == geom.geom_type:
            geom = simple
    data = json.loads(geom.json)
    data.pop("crs", None)
    if data["type"] == "Polygon":
        polygons = [data["coordinates"]]
    elif data["type"] == "MultiPolygon":
        polygons = data["coordinates"]
    else:
        return data
    if simplify:
        polygons = [_round(polygon, DISPLAY_DECIMALS) for polygon in polygons]
    polygons = [_orient(polygon) for polygon in polygons]
    data["coordinates"] = polygons[0] if data["type"] == "Polygon" else polygons
    return data