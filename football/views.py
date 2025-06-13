import hashlib

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from accounts.permissions import IsFieldOwner, IsAdminUser
from football.serializers import FootballFieldSerializer
from football.models import FootballField
from football.pagination import FootballPageNumberPagination
from django.core.cache import cache
from django.utils import timezone


class FootballFieldModelViewSet(ModelViewSet):
    serializer_class = FootballFieldSerializer
    queryset = FootballField.objects.all()
    pagination_class = FootballPageNumberPagination

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ['list']:
            raw_key = f"football_fields:{timezone.now()}"
            key = hashlib.md5(raw_key.encode()).hexdigest()
            cached_page = cache.get(key)

            if cached_page:
                return cached_page

            cache.set(key, queryset, timeout=60 * 1)

        return queryset

    def get_permissions(self):
        if self.action in ['list', "retrieve"]:
            return [AllowAny()]
        if self.action in ["update", "destroy"]:
            return [IsFieldOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
