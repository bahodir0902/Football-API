from rest_framework.permissions import BasePermission
from football.models import FootballField
from django.contrib.auth.models import Group

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        admin_group, _ = Group.objects.get_or_create(name='Admins')
        if user.is_superuser or user.is_staff or user.groups.all().first() == admin_group:
            return True
        return bool(
            user and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )


class IsFieldOwner(BasePermission):
    def has_object_permission(self, request, view, obj: FootballField):
        user = request.user
        admin_group, _ = Group.objects.get_or_create(name='Admins')
        if user.is_superuser or user.is_staff or user.groups.all().first() == admin_group:
            return True
        return bool(
            user and user.is_authenticated
            and (obj.owner == user)

        )
