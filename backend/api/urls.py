from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.MeView.as_view(), name="me"),
    path("carriers/", views.CarrierListView.as_view(), name="carrier-list"),
    path("vehicles/", views.VehicleListView.as_view(), name="vehicle-list"),
    path("geocode/", views.GeocodeView.as_view(), name="geocode"),
    path("route/", views.RouteView.as_view(), name="route"),
    path("hours/", views.HoursView.as_view(), name="hours"),
    path("trips/plan/", views.TripPlanView.as_view(), name="trip-plan"),
    path("trips/", views.TripListView.as_view(), name="trip-list"),
    path("trips/<int:pk>/", views.TripDetailView.as_view(), name="trip-detail"),
]
