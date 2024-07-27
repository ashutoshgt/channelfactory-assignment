from django.urls import path

from geo import views

urlpatterns = [
    path("distance", views.distance),
]
