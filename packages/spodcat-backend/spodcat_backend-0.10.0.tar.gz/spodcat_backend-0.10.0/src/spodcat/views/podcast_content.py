from typing import TypeVar, cast
from uuid import UUID

from django.apps import apps
from django.db.models import Q
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_json_api import views

from spodcat.filters import IdListFilter
from spodcat.models import PodcastContent
from spodcat.models.querysets import PodcastContentQuerySet
from spodcat.views.mixins import LogRequestMixin, PreloadIncludesMixin


_MT_co = TypeVar("_MT_co", bound=PodcastContent, covariant=True)


class PodcastContentFilter(IdListFilter):
    freetext = filters.CharFilter(method="filter_freetext")
    podcast = filters.CharFilter(method="filter_podcast")

    def filter_content(self, queryset, name, value):
        try:
            uuid = UUID(hex=value)
            return queryset.filter(Q(slug=value) | Q(pk=uuid))
        except ValueError:
            return queryset.filter(slug=value)

    def filter_podcast(self, queryset, name, value):
        return queryset.filter(podcast__slug=value)


class AbstractPodcastContentViewSet(LogRequestMixin, PreloadIncludesMixin, views.ReadOnlyModelViewSet[_MT_co]):
    select_for_includes = {
        "season": ["season__podcast"],
        "__all__": ["podcast"],
    }

    def filter_queryset(self, queryset):
        queryset = cast(PodcastContentQuerySet, super().filter_queryset(queryset))
        if self.action == "list":
            return queryset.listed()
        return queryset.published()

    @extend_schema(responses={(200, "text/plain"): OpenApiTypes.NONE})
    @action(methods=["post"], detail=True)
    def ping(self, request: Request, pk: str):
        instance = self.get_object()

        if apps.is_installed("spodcat.logs"):
            from spodcat.logs.models import PodcastContentRequestLog
            self.log_request(request, PodcastContentRequestLog, content=instance)

        return Response()
