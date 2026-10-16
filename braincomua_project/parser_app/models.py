from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    source_url = models.URLField(max_length=1000, blank=True)
    title = models.TextField()
    color = models.CharField(
        max_length=100,
        null=True,
    )
    storage_capacity = models.CharField(
        max_length=100,
        null=True,
    )
    manufacturer = models.CharField(
        max_length=100,
        null=True,
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    images = models.JSONField(default=list)

    product_code = models.CharField(
        max_length=100,
        null=True,
        db_index=True,
        verbose_name="Код товара",
    )
    reviews_count = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    screen_diagonal_inches = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    screen_resolution = models.CharField(
        max_length=100,
        null=True,
    )

    specifications = models.JSONField(
        default=None,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
