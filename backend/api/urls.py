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
    path("trips/", views.TripListCreateView.as_view(), name="trip-list-create"),
    path("trips/<int:pk>/", views.TripDetailView.as_view(), name="trip-detail"),
]
