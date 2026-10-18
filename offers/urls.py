from django.urls import path
from . import views

app_name = "offers"
urlpatterns = [
    path("", views.explore, name="explore"),
    path("popular/", views.popular, name="popular"),
    path("mentors/", views.mentors, name="mentors"),
    path("categories/", views.category_list, name="categories"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),
    path("offers/new/", views.create, name="create"),
    path("offers/mine/", views.my_offers, name="my_offers"),
    path("offers/<int:pk>/", views.detail, name="detail"),
    path("offers/<int:pk>/edit/", views.edit, name="edit"),
    path("offers/<int:pk>/delete/", views.delete, name="delete"),
    path("offers/<int:pk>/moderate/<str:action>/", views.moderate, name="moderate"),
]
