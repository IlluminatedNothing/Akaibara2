from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ROLE_ADMIN = 'admin'
    ROLE_CASHIER = 'cashier'
    ROLE_INSPECTOR = 'inspector'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_CASHIER, 'Cashier'),
        (ROLE_INSPECTOR, 'Inspector'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CASHIER,
    )

    phone = models.CharField(max_length=15, blank=True)


    def __str__(self):
        return f"{self.user.username} - {self.role}"

