from django.urls import path
from rest_framework.routers import DefaultRouter
from football.views import FootballFieldModelViewSet

router = DefaultRouter()
router.register('', FootballFieldModelViewSet, basename="footballs")

app_name = "football"
urlpatterns = [

] + router.urls


