from django.urls import path

from geo import views

urlpatterns = [
    path("hello", views.hello_world),
]
