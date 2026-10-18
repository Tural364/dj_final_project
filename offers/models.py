from django.conf import settings
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class SkillOffer(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
    class Format(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skill_offers")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="offers")
    title = models.CharField(max_length=140)
    description = models.TextField()
    image = models.ImageField(upload_to="offers/", blank=True, null=True)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.ONLINE)
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("offers:detail", kwargs={"pk": self.pk})
