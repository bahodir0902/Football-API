from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from accounts.permissions import IsFieldOwner, IsAdminUser
from football.serializers import FootballFieldSerializer
from football.models import FootballField
from football.pagination import FootballPageNumberPagination


class FootballFieldModelViewSet(ModelViewSet):
    serializer_class = FootballFieldSerializer
    queryset = FootballField.objects.all()
    pagination_class = FootballPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', "retrieve"]:
            return [AllowAny()]
        if self.action in ["update", "destroy"]:
            return [IsFieldOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
