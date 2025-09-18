r"""The translation models of the DataFrame components."""

# Local
from cambiato.models.core import BaseModel


class EditOrdersDataFrameValidationMessages(BaseModel):
    r"""Validation messages for the `edit_orders` DataFrame component."""

    duplicate_scheduled_start_time: str
    scheduled_end_time_le_start_time: str


class EditOrdersDataFrame(BaseModel):
    r"""The translation for the `edit_orders` DataFrame component."""

    c_order_id: str
    c_assigned_to_displayname: str
    c_scheduled_start_at: str
    c_scheduled_end_at: str
    c_order_status_name: str
    c_order_type_name: str
    c_facility_ean: str
    c_address: str
    c_ext_id: str
    c_description: str
    c_created_by: str
    c_created_at: str
    c_updated_by: str
    c_updated_at: str
    validation_messages: EditOrdersDataFrameValidationMessages


class DataFrames(BaseModel):
    r"""The translations of the DataFrame components."""

    edit_orders: EditOrdersDataFrame
