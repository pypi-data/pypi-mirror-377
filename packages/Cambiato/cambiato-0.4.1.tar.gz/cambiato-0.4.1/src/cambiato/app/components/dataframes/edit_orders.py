r"""The `edit_orders` component to edit multiple orders in DataFrame mode."""

# Standard library
from typing import Literal, TypeAlias

# Third party
import pandas as pd
import streamlit as st
from streamlit.column_config import (
    DatetimeColumn,
    NumberColumn,
    SelectboxColumn,
    TextColumn,
)

# Local
from cambiato.app.components.icons import ICON_ERROR
from cambiato.app.components.keys import EDIT_ORDERS_DATAFRAME_EDITOR
from cambiato.core import OperationResult
from cambiato.models.dataframe import (
    FacilityDataFrameModel,
    OrderDataFrameModel,
    OrderStatusDataFrameModel,
    OrderTypeDataFrameModel,
    UserDataFrameModel,
)
from cambiato.translations import EditOrdersDataFrame, EditOrdersDataFrameValidationMessages

ScheduledAt: TypeAlias = Literal['datetime', 'date']


def _validate_duplicate_start_time(
    df: pd.DataFrame, schedule_datetime_type: ScheduledAt, error_msg: str
) -> OperationResult:
    r"""Check for duplicate scheduled start times for a technician.

    A technician should not have an order scheduled at the exact same start time.
    If a date is used for the scheduled start time the validation is omitted.
    A technician can have multiple orders scheduled for the same day.

    Parameters
    ----------
    df : pandas.DataFrame
        The edited DataFrame to validate.

    schedule_datetime_type : Literal['datetime', 'date']
        Specify 'datetime' if the column "scheduled_start_at" contains timestamps and
        the validation should be triggered. If 'date' the validation is omitted.

    error_msg : str
        The validation error message.

    Returns
    -------
    cambiato.OperationResult
        The result of the validation.
    """

    if schedule_datetime_type == 'date':
        return OperationResult(ok=True)

    model = OrderDataFrameModel
    c_start_at = model.c_scheduled_start_at
    c_technician = model.c_assigned_to_displayname
    cols = [c_start_at, c_technician]

    mask = df[~df[c_start_at].isna() & ~df[c_technician].isna()].duplicated(subset=cols, keep=False)
    duplicated_order_ids = mask[mask.eq(True)].index
    df_duplicates = df.loc[duplicated_order_ids, cols]

    if df_duplicates.shape[0] == 0:
        return OperationResult(ok=True)

    start_time = df_duplicates[c_start_at].unique()[0]
    technician = df_duplicates[c_technician].unique()[0]
    order_ids = ', '.join(str(i) for i in duplicated_order_ids)

    return OperationResult(
        ok=False,
        short_msg=error_msg.format(
            start_time=start_time, technician=technician, order_ids=order_ids
        ),
    )


def _validate_scheduled_start_and_end_time(
    df: pd.DataFrame, schedule_datetime_type: ScheduledAt, error_msg: str
) -> OperationResult:
    r"""Validate that the scheduled start time is < scheduled end time.

    Parameters
    ----------
    df : pandas.DataFrame
        The edited DataFrame to validate.

    schedule_datetime_type : Literal['datetime', 'date']
        Specify 'datetime' if the columns "scheduled_start_at" and "scheduled_end_at" contain
        timestamps and the validation should be triggered. If 'date' the validation is omitted.

    error_msg : str
        The validation error message.

    Returns
    -------
    cambiato.OperationResult
        The result of the validation.
    """

    if schedule_datetime_type == 'date':
        return OperationResult(ok=True)

    model = OrderDataFrameModel
    c_start_at = model.c_scheduled_start_at
    c_end_at = model.c_scheduled_end_at

    mask = ~df[c_start_at].isna() & ~df[c_end_at].isna()
    df_invalid = df[mask][df[c_end_at].le(df[c_start_at])]

    if df_invalid.shape[0] == 0:
        return OperationResult(ok=True)

    return OperationResult(
        ok=False, short_msg=error_msg.format(order_ids=', '.join(str(i) for i in df_invalid.index))
    )


def _validate_edited_df(
    df: pd.DataFrame,
    schedule_datetime_type: ScheduledAt,
    trans: EditOrdersDataFrameValidationMessages,
) -> tuple[OperationResult, ...]:
    r"""Validate that the edited DataFrame is still in a valid state after edits.

    Parameters
    ----------
    df : pandas.DataFrame
        The edited DataFrame to validate.

    schedule_datetime_type : Literal['datetime', 'date']
        Specify 'datetime' if the columns "scheduled_start_at" and "scheduled_end_at" contain
        timestamps and the validation should be triggered. If 'date' the validation is omitted.

    trans : cambiato.translations.EditOrdersDataFrameValidationMessages
        The translations of the validation error messages.

    Returns
    -------
    tuple[cambiato.OperationResult, ...]
        The results of the applied validations.
    """

    r1 = _validate_duplicate_start_time(
        df=df,
        schedule_datetime_type=schedule_datetime_type,
        error_msg=trans.duplicate_scheduled_start_time,
    )
    r2 = _validate_scheduled_start_and_end_time(
        df=df,
        schedule_datetime_type=schedule_datetime_type,
        error_msg=trans.scheduled_end_time_le_start_time,
    )

    return r1, r2


def edit_orders(
    orders: OrderDataFrameModel,
    order_types: OrderTypeDataFrameModel,
    order_statuses: OrderStatusDataFrameModel,
    facilities: FacilityDataFrameModel,
    technicians: UserDataFrameModel,
    trans: EditOrdersDataFrame,
    schedule_datetime_type: ScheduledAt = 'date',
    editable: bool = True,
    allow_insert_and_delete: bool = False,
    datetime_format: str | None = 'YYYY-MM-DD HH:mm:ss',
    date_format: str | None = 'YYYY-MM-DD',
    key: str = EDIT_ORDERS_DATAFRAME_EDITOR,
) -> tuple[bool, OrderDataFrameModel]:
    r"""Edit orders in DataFrame mode.

    Useful to make updates to multiple orders at once.

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

    checklists : cambiato.models.ChecklistDataFrameModel
        The selectable checklists that can be assigned to an order.

    technicians : cambiato.models.UserDataFrameModel
        The selectable technicians that can be assigned to an order.

    trans : cambiato.translations.EditOrdersDataFrame
        The translations for the DataFrame and validation error messages.

    schedule_datetime_type : Literal['date', 'datetime'], default 'date'
        If the "scheduled_start_at" and "scheduled_end_at" columns should be
        rendered as date or datetime columns respectively.

    editable : bool, default True
        True if the DataFrame columns should be editable and False otherwise.

    allow_insert_and_delete: bool, default False
        True if the user should be able to add and delete rows and False otherwise.

    datetime_format : str or None, default 'YYYY-MM-DD HH:mm:ss'
        The format of the datetime columns. When `schedule_datetime_type` is set to 'date'
        `date_format` is applied to the columns "scheduled_start_at" and "scheduled_end_at".
        Uses the momentJS formatting language. If None the Streamlit default format is used.

    date_format : str or None, default 'YYYY-MM-DD'
        The format of the columns "scheduled_start_at" and "scheduled_end_at" when
        `schedule_datetime_type` is set to 'date'. Uses the momentJS formatting language.
        If None the Streamlit default format is used.

    key : str, default cambiato.app.components.EDIT_ORDERS_DATAFRAME_EDITOR
        The unique identifier of the modified state of the DataFrame in the session state.

    Returns
    -------
    bool
        True if the edited DataFrame is in a valid state after user edits and False otherwise.

    cambiato.models.OrderDataFrameModel
        A model of the updated state of the orders after user edits.
    """

    scheduled_format = datetime_format if schedule_datetime_type == 'datetime' else date_format
    column_config = {
        '_index': NumberColumn(label=trans.c_order_id, disabled=True),
        orders.c_assigned_to_displayname: SelectboxColumn(
            label=trans.c_assigned_to_displayname,
            options=technicians.get_column(technicians.c_displayname),
        ),
        orders.c_scheduled_start_at: DatetimeColumn(
            label=trans.c_scheduled_start_at, format=scheduled_format, pinned=False
        ),
        orders.c_scheduled_end_at: DatetimeColumn(
            label=trans.c_scheduled_end_at, format=scheduled_format, pinned=False
        ),
        orders.c_order_status_name: SelectboxColumn(
            label=trans.c_order_status_name,
            options=order_statuses.get_column(order_statuses.c_name),
            required=True,
        ),
        orders.c_order_type_name: SelectboxColumn(
            label=trans.c_order_type_name,
            options=order_types.get_column(order_types.c_name),
            required=True,
        ),
        orders.c_facility_ean: SelectboxColumn(
            label=trans.c_facility_ean, options=facilities.get_column(facilities.c_ean)
        ),
        orders.c_address: TextColumn(label=trans.c_address, disabled=True),
        orders.c_ext_id: TextColumn(label=trans.c_ext_id, disabled=False),
        orders.c_description: TextColumn(label=trans.c_description, disabled=False),
        orders.c_created_by: TextColumn(label=trans.c_created_by, disabled=True),
        orders.c_created_at: DatetimeColumn(
            label=trans.c_created_at, format=datetime_format, disabled=True
        ),
        orders.c_updated_by: TextColumn(label=trans.c_updated_by, disabled=True),
        orders.c_updated_at: DatetimeColumn(
            label=trans.c_updated_at, format=datetime_format, disabled=True
        ),
    }
    column_order = (
        orders.c_assigned_to_displayname,
        orders.c_scheduled_start_at,
        orders.c_scheduled_end_at,
        orders.c_order_status_name,
        orders.c_order_type_name,
        orders.c_facility_ean,
        orders.c_address,
        orders.c_ext_id,
        orders.c_description,
        orders.c_created_by,
        orders.c_created_at,
        orders.c_updated_by,
        orders.c_updated_at,
    )

    banner_container = st.container(key='edit-orders-banner-container')
    edited_df = st.data_editor(
        orders.df,
        hide_index=False,
        column_config=column_config,
        column_order=column_order,
        disabled=not editable,
        num_rows='dynamic' if allow_insert_and_delete else 'fixed',
        key=key,
    )

    if not editable:
        return True, OrderDataFrameModel(df=edited_df)

    results = _validate_edited_df(
        df=edited_df,
        schedule_datetime_type=schedule_datetime_type,
        trans=trans.validation_messages,
    )

    is_valid = True
    for r in results:
        if r.ok:
            continue
        banner_container.error(r.short_msg, icon=ICON_ERROR)
        is_valid = False

    return is_valid, OrderDataFrameModel(df=edited_df)
