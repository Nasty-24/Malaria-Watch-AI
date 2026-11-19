from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework import generics

from apps.core.pagination import StandardPagination

from .filters import RegionFilter
from .geojson import DisplayGeoJSON
from .models import Country, Region
from .serializers import CountrySerializer, RegionSerializer


class RegionPagination(StandardPagination):
    max_page_size = 50  # boundaries can be large payloads


class CountryListView(generics.ListAPIView):
    """Supported countries. Add include_boundary=true for the country boundary."""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = None
    filter_backends = []


@method_decorator(gzip_page, name="dispatch")  # public geometry only, no secrets in the body
class RegionListView(generics.ListAPIView):
    """Administrative regions. Filters: country, level, search. Add include_boundary=false to omit geometry.

    Boundaries in this list are simplified for display; GET regions/{id}/ returns the full boundary.
    """

    queryset = Region.objects.select_related("country")
    serializer_class = RegionSerializer
    filterset_class = RegionFilter
    pagination_class = RegionPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("include_boundary", "true").lower() == "false":
            return queryset.defer("boundary")
        # Simplify in PostGIS so full-resolution polygons never leave the database.
        return queryset.annotate(display_boundary=DisplayGeoJSON("boundary")).defer("boundary")

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "simplify_boundary": True}


class RegionDetailView(generics.RetrieveAPIView):
    queryset = Region.objects.select_related("country")
    serializer_class = RegionSerializer