from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"
        SUPER_ADMIN = "super_admin", "Super Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    bio = models.CharField(max_length=300, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_blocked = models.BooleanField(default=False)

    @property
    def is_platform_admin(self):
        return self.is_superuser or self.role in (self.Role.ADMIN, self.Role.SUPER_ADMIN)

    def __str__(self):
        return self.username
