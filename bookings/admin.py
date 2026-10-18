from django.contrib import admin
from .models import BookingRequest

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("offer", "learner", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("offer__title", "learner__username")
