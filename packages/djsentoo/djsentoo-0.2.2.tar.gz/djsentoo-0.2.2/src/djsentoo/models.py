from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class CurrencyChoices(models.TextChoices):
    ANG = "ANG", _("Netherlands Antillean Guilder")
    AWG = "AWG", _("Aruban Florin")
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")
    XCG = "XCG", _("East Caribbean Guilder")


class TransactionStatusChoices(models.TextChoices):
    ISSUED = "issued", _("Issued")
    FAILED = "failed", _("Failed")
    PENDING = "pending", _("Pending")
    SUCCESS = "success", _("Success")
    EXPIRED = "expired", _("Expired")
    CANCELLED = "cancelled", _("Cancelled")


class Transaction(models.Model):
    status = models.CharField(
        max_length=20,
        choices=TransactionStatusChoices.choices,
        default=TransactionStatusChoices.ISSUED,
        db_index=True,
    )
    amount = models.IntegerField(default=0)
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.XCG,
        db_index=True,
    )
    merchant_id = models.CharField(max_length=46)
    description = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255, db_index=True)
    return_url = models.CharField(max_length=255)
    customer = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    @property
    def decimal_amount(self) -> Decimal:
        return Decimal(self.amount) / 100

    def __str__(self):
        return f"{self.currency} {self.decimal_amount}"
