r"""The translation models of the pages.

These models group the translations for the components, views, controllers
and database objects that a page needs.
"""

# Local
from cambiato.models.core import BaseModel
from cambiato.translations.components import CreateOrderButton, CreateOrderForm, EditOrdersDataFrame
from cambiato.translations.controllers import OrderController
from cambiato.translations.database import Database
from cambiato.translations.views import EditOrdersView


class OrderPage(BaseModel):
    r"""The translations for the order page."""

    controller: OrderController
    db: Database
    create_order_button: CreateOrderButton
    create_order_form: CreateOrderForm
    edit_orders_df: EditOrdersDataFrame
    edit_orders_view: EditOrdersView


class PageTranslationModels(BaseModel):
    r"""The translation models of the pages."""

    order_page: OrderPage
