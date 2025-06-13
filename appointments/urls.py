from django.urls import path
from rest_framework.routers import DefaultRouter
from appointments.views import AppointmentViewSet

router = DefaultRouter()
router.register("", AppointmentViewSet, basename='appointment')

app_name = "appointments"

urlpatterns = [

] + router.urls


