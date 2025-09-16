from django.contrib import admin

from djsentoo.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_filter = ("status", "currency", "created_at")
    list_display = ("transaction_id", "status", "amount", "currency", "created_at")
    search_fields = ("transaction_id", "customer")
    readonly_fields = (
        "transaction_id",
        "merchant_id",
        "return_url",
        "status",
        "amount",
        "currency",
        "customer",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=...):
        return False
