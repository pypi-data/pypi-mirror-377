r"""The core component that includes all views translation models."""

# Local
from cambiato.models.core import BaseModel

from .orders import Orders


class Views(BaseModel):
    r"""The translations of the views."""

    orders: Orders
