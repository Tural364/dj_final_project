from django.urls import path
from . import views

app_name = "bookings"
urlpatterns = [
    path("", views.mine, name="mine"),
    path("new/<int:offer_id>/", views.create, name="create"),
    path("<int:pk>/<str:action>/", views.update_status, name="update_status"),
]
