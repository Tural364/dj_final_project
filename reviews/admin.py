from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "author", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("author__username", "comment", "booking__offer__title")
