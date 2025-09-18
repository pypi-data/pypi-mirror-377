r"""The components that make up the web app."""

# Local
from cambiato.app.components.buttons import ButtonType, create_order_button, sign_out_button
from cambiato.app.components.core import (
    BannerContainer,
    BannerContainerMapping,
    LabelVisibility,
    process_form_validation_errors,
)
from cambiato.app.components.dataframes import ChangedDataFrameRows, edit_orders
from cambiato.app.components.forms import create_order_form
from cambiato.app.components.icons import ICON_ERROR, ICON_INFO, ICON_SUCCESS, ICON_WARNING
from cambiato.app.components.keys import (
    CREATE_ORDER_BUTTON,
    CREATE_ORDER_FORM,
    CREATE_ORDER_FORM_CHECKLIST_SELECTBOX,
    CREATE_ORDER_FORM_DESCRIPTION_TEXT_AREA,
    CREATE_ORDER_FORM_EXT_ID_TEXT_INPUT,
    CREATE_ORDER_FORM_FACILITY_SELECTBOX,
    CREATE_ORDER_FORM_ORDER_STATUS_SELECTBOX,
    CREATE_ORDER_FORM_ORDER_TYPE_SELECTBOX,
    CREATE_ORDER_FORM_SCHEDULED_DAY_DATE_INPUT,
    CREATE_ORDER_FORM_SCHEDULED_END_TIME_INPUT,
    CREATE_ORDER_FORM_SCHEDULED_START_TIME_INPUT,
    CREATE_ORDER_FORM_TECHNICIAN_SELECTBOX,
    EDIT_ORDERS_DATAFRAME_EDITOR,
    UTILITY_PILLS_SELECTOR,
)
from cambiato.app.components.selectors import utility_pills_selector
from cambiato.app.components.sidebar import sidebar

# The Public API
__all__ = [
    # buttons
    'ButtonType',
    'create_order_button',
    'sign_out_button',
    # core
    'BannerContainer',
    'BannerContainerMapping',
    'LabelVisibility',
    'process_form_validation_errors',
    # dataframes
    'ChangedDataFrameRows',
    'edit_orders',
    # forms
    'create_order_form',
    # icons
    'ICON_ERROR',
    'ICON_INFO',
    'ICON_SUCCESS',
    'ICON_WARNING',
    # keys
    'CREATE_ORDER_BUTTON',
    'CREATE_ORDER_FORM',
    'CREATE_ORDER_FORM_CHECKLIST_SELECTBOX',
    'CREATE_ORDER_FORM_DESCRIPTION_TEXT_AREA',
    'CREATE_ORDER_FORM_EXT_ID_TEXT_INPUT',
    'CREATE_ORDER_FORM_FACILITY_SELECTBOX',
    'CREATE_ORDER_FORM_ORDER_STATUS_SELECTBOX',
    'CREATE_ORDER_FORM_ORDER_TYPE_SELECTBOX',
    'CREATE_ORDER_FORM_SCHEDULED_DAY_DATE_INPUT',
    'CREATE_ORDER_FORM_SCHEDULED_END_TIME_INPUT',
    'CREATE_ORDER_FORM_SCHEDULED_START_TIME_INPUT',
    'CREATE_ORDER_FORM_TECHNICIAN_SELECTBOX',
    'EDIT_ORDERS_DATAFRAME_EDITOR',
    'UTILITY_PILLS_SELECTOR',
    # sidebar
    'sidebar',
    # selectors
    'utility_pills_selector',
]
