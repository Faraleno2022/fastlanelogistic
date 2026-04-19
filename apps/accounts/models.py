from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        DIRECTION = "DIRECTION", "Direction"
        COMPTABLE = "COMPTABLE", "Comptable"
        RH = "RH", "Responsable RH"
        EXPLOITATION = "EXPLOITATION", "Chef d'exploitation"
        POINTEUR = "POINTEUR", "Pointeur / Agent"
        ATELIER = "ATELIER", "Atelier / Maintenance"

    role = models.CharField(
        "Rôle", max_length=20,
        choices=Role.choices, default=Role.POINTEUR,
    )
    telephone = models.CharField("Téléphone", max_length=30, blank=True)
    site = models.CharField("Site", max_length=80, blank=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        full = self.get_full_name()
        return full if full else self.username

    @property
    def is_direction(self):
        return self.role in {self.Role.ADMIN, self.Role.DIRECTION}

    @property
    def can_edit_finances(self):
        return self.role in {self.Role.ADMIN, self.Role.DIRECTION, self.Role.COMPTABLE}
