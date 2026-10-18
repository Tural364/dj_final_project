from django.contrib import admin
from .models import Category, SkillOffer

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(SkillOffer)
class SkillOfferAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "status", "created_at")
    list_filter = ("status", "category", "level", "format")
    search_fields = ("title", "description", "owner__username")
    actions = ["publish_offers", "reject_offers"]

    @admin.action(description="Approve selected offers")
    def publish_offers(self, request, queryset):
        queryset.update(status=SkillOffer.Status.PUBLISHED)

    @admin.action(description="Reject selected offers")
    def reject_offers(self, request, queryset):
        queryset.update(status=SkillOffer.Status.REJECTED)
