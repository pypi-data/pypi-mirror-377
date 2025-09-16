from copy import deepcopy
from typing import Any

from django.conf import settings

SENTOO_DEFAULTS = {
    "SECRET": None,
    "SANDBOX": True,
    "MERCHANT_ID": None,
    "DEFAULT_CURRENCY": "XCD",
}


def get_sentoo_settings() -> dict[str, Any]:
    """
    Returns the settings for Sentoo payment gateway.
    """
    settings_copy = deepcopy(SENTOO_DEFAULTS)
    if hasattr(settings, "SENTOO"):
        assert isinstance(settings.SENTOO, dict)
        settings_copy.update(**settings.SENTOO)

    return settings_copy
