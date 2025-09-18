r"""The language translation models of the page controllers."""

# Local
from cambiato.models.core import BaseModel


class OrderController(BaseModel):
    r"""The translations of the order page controller."""

    page_title: str
    select_utility_info_message: str


class Controllers(BaseModel):
    r"""The translations of the page controllers."""

    order: OrderController
