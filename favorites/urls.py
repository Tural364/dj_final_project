from django.urls import path
from . import views

app_name = "favorites"
urlpatterns = [
    path("", views.list_favorites, name="list"),
    path("toggle/<int:offer_id>/", views.toggle, name="toggle"),
]
