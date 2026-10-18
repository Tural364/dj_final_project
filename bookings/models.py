from django.conf import settings
from django.db import models
from offers.models import SkillOffer

class BookingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    offer = models.ForeignKey(SkillOffer, on_delete=models.CASCADE, related_name="booking_requests")
    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_booking_requests")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["offer", "learner"], condition=models.Q(status__in=["pending", "accepted"]), name="unique_active_booking_per_offer_learner")
        ]

    def __str__(self):
        return f"{self.learner} → {self.offer} ({self.status})"
