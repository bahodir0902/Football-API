from rest_framework.permissions import BasePermission
from appointments.models import Appointment
from django.contrib.auth.models import Group

class IsAppointmentOwner(BasePermission):
    def has_object_permission(self, request, view, obj: Appointment):
        user = request.user
        admin_group, _ = Group.objects.get_or_create(name='Admins')
        if user.is_superuser or user.is_staff or user.groups.all().first() == admin_group:
            return True
        return bool(
            user and user.is_authenticated
            and (obj.user == user)

        )
