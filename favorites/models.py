from django.conf import settings
from django.db import models
from offers.models import SkillOffer

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    offer = models.ForeignKey(SkillOffer, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "offer"], name="unique_user_favorite_offer")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.offer}"
