r"""The view `edit_orders_view` to edit multiple orders in DataFrame mode."""

# Standard library
from collections.abc import Callable
from datetime import UTC, datetime, time
from functools import partial
from time import sleep
from zoneinfo import ZoneInfo

# Third party
import streamlit as st

# Local
from cambiato.app.components import (
    EDIT_ORDERS_DATAFRAME_EDITOR,
    ICON_SUCCESS,
    ChangedDataFrameRows,
    edit_orders,
)
from cambiato.app.database import get_all_orders_cached
from cambiato.database import ChangedDatabaseRows, Session, process_changed_orders
from cambiato.models import (
    FacilityDataFrameModel,
    OrderDataFrameModel,
    OrderStatusDataFrameModel,
    OrderTypeDataFrameModel,
    UserDataFrameModel,
)
from cambiato.translations import EditOrdersDataFrame, EditOrdersView


def _str_to_utc_timestamp(value: str | None, tz: ZoneInfo, is_date: bool) -> datetime | None:
    r"""Convert a timestamp string into a UTC timestamp.

    Parameters
    ----------
    value : str or None
        The timestamp string in isoformat to convert into a UTC timestamp.

    is_date : bool
        True if the `value` should be interpreted as a date and False for a timestamp.

    tz : zoneinfo.ZoneInfo
        The timezone of `value`.

    Returns
    -------
    datetime or None
        The UTC timestamp or None if `value` is None.
    """

    if value is None:
        return value

    timestamp = datetime.fromisoformat(value)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=tz)

    if is_date:
        return datetime.combine(timestamp.astimezone(tz), time(0, 0), tzinfo=tz).astimezone(UTC)

    return timestamp.astimezone(UTC)


def _get_self(value: str) -> str:
    r"""Return the input `value`."""

    return value


def _process_edited_orders(
    edited_orders: ChangedDataFrameRows,
    orders: OrderDataFrameModel,
    order_types: OrderTypeDataFrameModel,
    order_statuses: OrderStatusDataFrameModel,
    facilities: FacilityDataFrameModel,
    technicians: UserDataFrameModel,
    scheduled_is_date: bool,
    tz: ZoneInfo,
    user_id: str,
) -> ChangedDatabaseRows:
    r"""Process the edited orders and prepare them for the database update.

    order_types : cambiato.models.OrderTypeDataFrameModel
        The selectable order types for looking up the primary key of the order_type table.

    order_statuses : cambiato.models.OrderStatusDataFrameModel
        The selectable order statuses for looking up the primary key of the order_status table.

    facilities : cambiato.models.FacilityDataFrameModel
        The selectable facilities for looking up the primary key of the facility table.

    technicians : cambiato.models.UserDataFrameModel
        The selectable technicians for looking up the primary key of the user table.

    scheduled_is_date : bool
        True if the "scheduled_start_at" and "scheduled_end_at" columns contain dates
        and False for timestamp values.

    tz : zoneinfo.ZoneInfo
        The timezone of the datetime columns that the user can edit.

    user_id : str
        The ID of the user performing the order updates.

    Returns
    -------
    cambiato.db.ChangedDatabaseRows
        The changed database rows to update.
    """

    to_utc = partial(_str_to_utc_timestamp, tz=tz, is_date=scheduled_is_date)

    column_converters: dict[
        str, tuple[str, Callable]
    ] = {  # column name : (column name to update, conversion function)
        orders.c_assigned_to_displayname: (
            orders.c_assigned_to_user_id,
            partial(technicians.get_index, column=technicians.c_displayname),
        ),
        orders.c_scheduled_start_at: (orders.c_scheduled_start_at, to_utc),
        orders.c_scheduled_end_at: (orders.c_scheduled_end_at, to_utc),
        orders.c_order_status_name: (
            orders.c_order_status_id,
            partial(order_statuses.get_index, column=order_statuses.c_name),
        ),
        orders.c_order_type_name: (
            orders.c_order_type_id,
            partial(order_types.get_index, column=order_types.c_name),
        ),
        orders.c_facility_ean: (
            orders.c_facility_id,
            partial(facilities.get_index, column=facilities.c_ean),
        ),
        orders.c_ext_id: (orders.c_ext_id, _get_self),
        orders.c_description: (orders.c_description, _get_self),
    }

    orders_to_update = [
        {'order_id': orders.get_index_by_row_nr(row_nr=int(row_nr))}
        | {
            conv[0]: conv[1](value)
            for col, value in row_content.items()
            if (conv := column_converters.get(col))
        }
        | {orders.c_updated_by: user_id}
        for row_nr, row_content in edited_orders['edited_rows'].items()
    ]

    return ChangedDatabaseRows(edited_rows=orders_to_update)


@st.fragment
def edit_orders_view(
    session: Session,
    orders: OrderDataFrameModel,
    order_types: OrderTypeDataFrameModel,
    order_statuses: OrderStatusDataFrameModel,
    facilities: FacilityDataFrameModel,
    technicians: UserDataFrameModel,
    trans: EditOrdersView,
    edit_orders_df_trans: EditOrdersDataFrame,
    tz: ZoneInfo,
    user_id: str,
    has_edit_permission: bool = False,
    schedule_entire_day_default: bool = True,
) -> None:
    r"""The view for listing and editing available orders.

    Parameters
    ----------
    orders : cambiato.models.OrderDataFrameModel
        The orders that can be edited.

    order_types : cambiato.models.OrderTypeDataFrameModel
        The selectable order types that can be assigned to an order.

    order_statuses : cambiato.models.OrderStatusDataFrameModel
        The selectable order statuses that can be assigned to an order.

    facilities : cambiato.models.FacilityDataFrameModel
        The selectable facilities that can be assigned to an order.

    technicians : cambiato.models.UserDataFrameModel
        The selectable technicians that can be assigned to an order.

    trans : cambiato.translations.EditOrdersView
        The translations for the view.

    edit_orders_df_trans : cambiato.translations.EditOrdersDataFrame
        The translations for the component :func:`cambiato.app.components.edit_orders`.

    tz : zoneinfo.ZoneInfo
        The timezone of the datetime columns that the user can edit.

    user_id : str
        The ID of the user editing the orders.

    has_edit_permission : bool, default False
        True if the user has permission to edit orders and False otherwise.

    schedule_entire_day_default : bool, default True
        True if the default should be to select a date when scheduling an order
        (i.e. schedule the entire day) and False to select a timestamp for the
        scheduled start and end time.

    Returns
    -------
    None
    """

    banner_container = st.empty()

    left_col, right_col, _ = st.columns([1, 2, 8])
    with left_col:
        save_changed_button_container = st.empty()

    with right_col:
        schedule_entire_day = st.toggle(
            label=trans.schedule_entire_day_toggle_label,
            value=schedule_entire_day_default,
            help=trans.schedule_entire_day_toggle_help,
        )

    edited_orders_are_valid, _ = edit_orders(
        orders=orders,
        order_types=order_types,
        order_statuses=order_statuses,
        technicians=technicians,
        facilities=facilities,
        trans=edit_orders_df_trans,
        schedule_datetime_type='date' if schedule_entire_day else 'datetime',
        editable=has_edit_permission,
    )

    modified_state = st.session_state.get(EDIT_ORDERS_DATAFRAME_EDITOR, {})
    rows_have_changed = any(v for v in modified_state.values())

    clicked = save_changed_button_container.button(
        label=trans.save_changes_button_label,
        type='primary',
        disabled=not rows_have_changed or not edited_orders_are_valid,
        key='edit-orders-section-save-changes-button',
    )

    if not clicked or not edited_orders_are_valid:
        return

    changed_orders = _process_edited_orders(
        edited_orders=modified_state,
        orders=orders,
        order_types=order_types,
        order_statuses=order_statuses,
        facilities=facilities,
        technicians=technicians,
        tz=tz,
        scheduled_is_date=schedule_entire_day,
        user_id=user_id,
    )

    result = process_changed_orders(session=session, changed_orders=changed_orders)

    if not result.ok:
        banner_container.error(result.short_msg)
        return

    banner_container.success(trans.update_orders_success_message, icon=ICON_SUCCESS)
    get_all_orders_cached.clear()  # type: ignore[attr-defined]
    sleep(1)
    st.rerun(scope='app')
