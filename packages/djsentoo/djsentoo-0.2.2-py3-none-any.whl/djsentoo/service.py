from dataclasses import dataclass
from functools import cache
from typing import Any

from sentoo import Sentoo

from djsentoo.config import get_sentoo_settings
from djsentoo.models import Transaction, TransactionStatusChoices
from djsentoo.signals import sentoo_transaction_created


@dataclass(frozen=True)
class CreatePaymentResponse:
    url: str
    qr_code_url: str
    transaction_id: str


@cache
def get_sentoo_client() -> Sentoo:
    config = get_sentoo_settings()
    return Sentoo(
        secret=config["SECRET"],
        sandbox=config["SANDBOX"],
        merchant_id=config["MERCHANT_ID"],
    )


class SentooPaymentService:
    def __init__(self) -> None:
        self._config = get_sentoo_settings()
        self._client = get_sentoo_client()

    def create_payment(
        self,
        amount: int,
        description: str,
        return_url: str,
        currency: str | None = None,
        customer: str | None = None,
    ) -> CreatePaymentResponse:
        request = {
            "sentoo_amount": amount,
            "sentoo_currency": currency,
            "sentoo_return_url": return_url,
            "sentoo_description": description,
        }
        if customer:
            request["sentoo_customer"] = customer

        res = self._client.transaction_create(**request)
        res.raise_for_status()

        data = res.json()

        qr_code_url = data["success"]["data"]["qr_code"]
        payment_url = data["success"]["data"]["url"]
        transaction_id = data["success"]["message"]

        created = self._create_database_transaction(
            {
                "sentoo_amount": amount,
                "sentoo_currency": currency or self._config["DEFAULT_CURRENCY"],
                "sentoo_return_url": return_url,
                "sentoo_description": description,
                "sentoo_customer": customer,
                "sentoo_transaction_id": transaction_id,
            }
        )

        sentoo_transaction_created.send(sender=None, transaction=created)
        return CreatePaymentResponse(
            url=payment_url,
            qr_code_url=qr_code_url,
            transaction_id=transaction_id,
        )

    def _create_database_transaction(self, request: dict[str, Any]) -> Transaction:
        transaction = Transaction.objects.create(
            status=TransactionStatusChoices.ISSUED,
            amount=request["sentoo_amount"],
            currency=request["sentoo_currency"],
            customer=request.get("sentoo_customer"),
            return_url=request["sentoo_return_url"],
            merchant_id=self._config["MERCHANT_ID"],
            description=request["sentoo_description"],
            transaction_id=request["sentoo_transaction_id"],
        )
        return transaction
