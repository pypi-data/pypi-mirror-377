from django import forms

from djsentoo.models import Transaction


class WebhookForm(forms.Form):
    transaction_id = forms.CharField(required=True, max_length=36)

    def clean_transaction_id(self):
        try:
            return Transaction.objects.get(transaction_id=self.cleaned_data["transaction_id"])
        except Transaction.DoesNotExist as exc:
            raise forms.ValidationError("Transaction does not exist") from exc
