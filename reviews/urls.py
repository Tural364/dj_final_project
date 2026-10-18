from django.urls import path
from . import views

app_name = "reviews"
urlpatterns = [
    path("new/<int:booking_id>/", views.create, name="create"),
    path("<int:pk>/edit/", views.edit, name="edit"),
    path("<int:pk>/delete/", views.delete, name="delete"),
]
