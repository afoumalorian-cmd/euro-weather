from django.conf import settings
from django.db import models


class FavoriteCity(models.Model):
    """
    Store a weather location saved by an authenticated user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_cities",
    )
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["city", "country"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "city",
                    "country",
                ],
                name="unique_favorite_city_per_user",
            ),
        ]
        verbose_name = "favorite city"
        verbose_name_plural = "favorite cities"

    def __str__(self):
        return f"{self.city}, {self.country} - {self.user}"