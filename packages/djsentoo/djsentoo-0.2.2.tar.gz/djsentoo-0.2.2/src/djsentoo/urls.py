from django.urls import path

from djsentoo.views import sentoo_webhook

app_name = "djsentoo"

urlpatterns = [
    path("webhook/", sentoo_webhook, name="transaction_status_webhook"),
]
