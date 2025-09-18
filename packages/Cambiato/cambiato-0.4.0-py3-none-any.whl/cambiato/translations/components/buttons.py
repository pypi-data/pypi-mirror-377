r"""The translation models of the button components."""

# Local
from cambiato.models.core import BaseModel


class CreateOrderButton(BaseModel):
    r"""The translation of the create order button."""

    label: str
    help_text: str | None = None


class Buttons(BaseModel):
    r"""The translations of the button components."""

    create_order_button: CreateOrderButton
