r"""The translation models of the order views."""

# Local
from cambiato.models.core import BaseModel


class EditOrdersView(BaseModel):
    r"""The translation for the view `edit_orders_view`."""

    save_changes_button_label: str
    schedule_entire_day_toggle_label: str
    schedule_entire_day_toggle_help: str
    update_orders_success_message: str


class Orders(BaseModel):
    r"""The translations of the order views."""

    edit_orders_view: EditOrdersView
