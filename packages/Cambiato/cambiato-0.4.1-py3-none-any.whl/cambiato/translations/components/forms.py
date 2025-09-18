r"""The translation models of the form components."""

# Local
from cambiato.models.core import BaseModel


class CreateOrderFormValidationMessage(BaseModel):
    r"""Validation messages for the create order form."""

    start_time_no_end_time: str
    end_time_no_start_time: str
    start_time_geq_end_time: str


class CreateOrderForm(BaseModel):
    r"""The translation of the create order form."""

    title: str
    department_id: str
    order_type_id_label: str
    order_type_id_placeholder: str
    order_status_id_label: str
    order_status_id_placeholder: str
    ext_id_label: str
    ext_id_placeholder: str
    facility_id_label: str
    facility_id_placeholder: str
    location_id_label: str
    location_id_placeholder: str
    checklist_id_label: str
    checklist_id_placeholder: str
    technician_id_label: str
    technician_id_placeholder: str
    description_label: str
    description_placeholder: str
    scheduled_date: str
    scheduled_start_at: str
    scheduled_end_at: str
    submit_button_label: str
    success_message: str
    error_message: str
    validation_messages: CreateOrderFormValidationMessage


class Forms(BaseModel):
    r"""The translations of the form components."""

    create_order_form: CreateOrderForm
