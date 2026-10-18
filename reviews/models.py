from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from bookings.models import BookingRequest

class Review(models.Model):
    booking = models.OneToOneField(BookingRequest, on_delete=models.CASCADE, related_name="review")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_written")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}/5 — {self.booking.offer.title}"
