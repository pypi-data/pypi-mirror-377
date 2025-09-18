r"""The create order form component."""

# Standard library
from datetime import UTC, date, datetime, time
from enum import StrEnum
from zoneinfo import ZoneInfo

# Third party
import streamlit as st

# Local
from cambiato.app.components import keys
from cambiato.app.components.core import BannerContainerMapping, process_form_validation_errors
from cambiato.app.components.icons import ICON_ERROR, ICON_SUCCESS
from cambiato.app.session_state import CREATE_ORDER_FORM_VALIDATION_ERRORS
from cambiato.database import Session, create_order, get_customer_id_by_facility_id
from cambiato.database.models import (
    Order,
)
from cambiato.models.dataframe import (
    ChecklistDataFrameModel,
    FacilityDataFrameModel,
    OrderStatusDataFrameModel,
    OrderTypeDataFrameModel,
    UserDataFrameModel,
)
from cambiato.translations import CreateOrderForm, CreateOrderFormValidationMessage


class FormField(StrEnum):
    r"""The fields of the create order form to validate."""

    SCHEDULED_START_TIME = 'scheduled_start_time'
    SCHEDULED_END_TIME = 'scheduled_end_time'


def _validate_form(translation: CreateOrderFormValidationMessage) -> None:
    r"""Validate the input fields of the create order form.

    Parameters
    ----------
    translation : cambiato.app.translation.CreateOrderFormValidationMessage
        The translations for the validation errors.
    """

    validation_errors = {}

    start_time = st.session_state[keys.CREATE_ORDER_FORM_SCHEDULED_START_TIME_INPUT]
    end_time = st.session_state[keys.CREATE_ORDER_FORM_SCHEDULED_END_TIME_INPUT]

    if start_time is None and end_time is None:
        pass

    elif start_time is None and end_time is not None:
        validation_errors[FormField.SCHEDULED_START_TIME] = translation.start_time_no_end_time

    elif start_time is not None and end_time is None:
        validation_errors[FormField.SCHEDULED_END_TIME] = translation.end_time_no_start_time

    elif start_time >= end_time:
        validation_errors[FormField.SCHEDULED_START_TIME] = (
            translation.start_time_geq_end_time.format(start_time=start_time, end_time=end_time)
        )

    else:
        pass

    st.session_state[CREATE_ORDER_FORM_VALIDATION_ERRORS] = validation_errors


def _create_scheduled_timestamps(
    day: date | None, start_time: time | None, end_time: time | None, tz: ZoneInfo
) -> tuple[datetime | None, datetime | None]:
    r"""Create the scheduled at interval.

    Parameters
    ----------
    day : datetime.date or None
        The date that the order is scheduled at. If None the order is not scheduled.

    start_time : datetime.time or None
        The time of `day` when the technician is expected to start working on the order.
        If None there is no specified start time.

    end_time : datetime.time or None
        The time of `day` when the order is expected to be completed.
        If None there is no end time.

    tz : zoneinfo.ZoneInfo
        The timezone in which `day`, `start_time` and `end_time` are specified.

    Returns
    -------
    start_datetime : datetime.datetime or None
        The scheduled start time. None if the order is not scheduled.

    end_datetime : datetime.datetime or None
        The scheduled end time. None if the end time is not scheduled.
    """

    if day:
        if start_time:
            start_datetime = datetime.combine(date=day, time=start_time, tzinfo=tz).astimezone(UTC)
        else:
            start_datetime = datetime.combine(date=day, time=time(0, 0), tzinfo=tz).astimezone(UTC)

        if end_time:
            end_datetime = datetime.combine(date=day, time=end_time, tzinfo=tz).astimezone(UTC)
        else:
            end_datetime = None
    else:
        start_datetime = None
        end_datetime = None

    return start_datetime, end_datetime


def create_order_form(
    session: Session,
    utility_id: int,
    order_types: OrderTypeDataFrameModel,
    order_statuses: OrderStatusDataFrameModel,
    facilities: FacilityDataFrameModel,
    checklists: ChecklistDataFrameModel,
    technicians: UserDataFrameModel,
    translation: CreateOrderForm,
    tz: ZoneInfo,
    user_id: str | None = None,
    border: bool = True,
    title: bool = True,
    key: str = keys.CREATE_ORDER_FORM,
) -> Order | None:
    r"""Render the form for creating an order.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    utility_id : int
        The primary key of the utility that the created order should belong to.

    order_types : cambiato.models.OrderTypeDataFrameModel
        The selectable order types of the order to create.

    order_statuses : cambiato.models.OrderStatusDataFrameModel
        The selectable order statuses of the order to create.

    facilities : cambiato.models.FacilityDataFrameModel
        The selectable facilities that can be assigned to the order.

    checklists : cambiato.models.ChecklistDataFrameModel
        The selectable checklists that can be assigned to the order.

    technicians : cambiato.models.UserDataFrameModel
        The selectable technicians that can be assigned to the order.

    translation : cambiato.translations.CreateOrderForm
        The language translations for the form.

    tz : zoneinfo.ZoneInfo
        The timezone of the entered datetime values of the form.

    user_id : str or None, default None
        The ID of the user that is creating the order.

    border : bool, default True
        True if a border should be rendered around the form and False for no border.

    title : bool, default True
        True if the title of the form should be rendered.
        Useful for removing the title if rendering the form in a dialog frame.

    key : str, default cambiato.app.components.keys.CREATE_ORDER_FORM
        The unique identifier of the form in the session state.
    """

    banner_container_mapping: BannerContainerMapping = {}

    with st.form(key=key, border=border):
        banner_container = st.empty()
        if title:
            st.markdown(f'### {translation.title}')

        order_type_id = st.selectbox(
            label=translation.order_type_id_label,
            placeholder=translation.order_type_id_placeholder,
            options=order_types.index,
            format_func=order_types.format_func,
            disabled=order_types.empty,
            key=keys.CREATE_ORDER_FORM_ORDER_TYPE_SELECTBOX,
        )
        order_status_id = st.selectbox(
            label=translation.order_status_id_label,
            placeholder=translation.order_status_id_placeholder,
            options=order_statuses.index,
            format_func=order_statuses.format_func,
            disabled=order_statuses.empty,
            key=keys.CREATE_ORDER_FORM_ORDER_STATUS_SELECTBOX,
        )
        facility_id = st.selectbox(
            label=translation.facility_id_label,
            placeholder=translation.facility_id_placeholder,
            options=facilities.index,
            format_func=facilities.format_func,
            index=None,
            disabled=facilities.empty,
            key=keys.CREATE_ORDER_FORM_FACILITY_SELECTBOX,
        )
        checklist_id = st.selectbox(
            label=translation.checklist_id_label,
            placeholder=translation.checklist_id_placeholder,
            options=checklists.index,
            index=None,
            format_func=checklists.format_func,
            disabled=checklists.empty,
            key=keys.CREATE_ORDER_FORM_CHECKLIST_SELECTBOX,
        )
        ext_id = st.text_input(
            label=translation.ext_id_label,
            placeholder=translation.ext_id_placeholder,
            key=keys.CREATE_ORDER_FORM_EXT_ID_TEXT_INPUT,
        )
        technician_id = st.selectbox(
            label=translation.technician_id_label,
            placeholder=translation.technician_id_placeholder,
            options=technicians.index,
            format_func=technicians.format_func,
            index=None,
            disabled=technicians.empty,
            key=keys.CREATE_ORDER_FORM_TECHNICIAN_SELECTBOX,
        )
        description = st.text_area(
            label=translation.description_label,
            placeholder=translation.description_placeholder,
            key=keys.CREATE_ORDER_FORM_DESCRIPTION_TEXT_AREA,
        )

        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            scheduled_day = st.date_input(
                label=translation.scheduled_date,
                value=None,
                format='YYYY-MM-DD',
                key=keys.CREATE_ORDER_FORM_SCHEDULED_DAY_DATE_INPUT,
            )
        with mid_col:
            banner_container_mapping[FormField.SCHEDULED_START_TIME] = st.empty()
            scheduled_start_time = st.time_input(
                label=translation.scheduled_start_at,
                value=None,
                key=keys.CREATE_ORDER_FORM_SCHEDULED_START_TIME_INPUT,
            )
        with right_col:
            banner_container_mapping[FormField.SCHEDULED_END_TIME] = st.empty()
            scheduled_end_time = st.time_input(
                label=translation.scheduled_end_at,
                value=None,
                key=keys.CREATE_ORDER_FORM_SCHEDULED_END_TIME_INPUT,
            )

        disabled = order_types.empty or order_statuses.empty or facilities.empty

        clicked = st.form_submit_button(
            label=translation.submit_button_label,
            type='primary',
            disabled=disabled,
            on_click=_validate_form,
            kwargs={'translation': translation.validation_messages},
        )

        if not clicked:
            return None

        if validation_errors := st.session_state.get(CREATE_ORDER_FORM_VALIDATION_ERRORS, {}):
            process_form_validation_errors(
                validation_errors=validation_errors,
                banner_container_mapping=banner_container_mapping,
            )
            st.session_state[CREATE_ORDER_FORM_VALIDATION_ERRORS] = {}

            return None

        start_datetime, end_datetime = _create_scheduled_timestamps(
            day=scheduled_day,
            start_time=scheduled_start_time,
            end_time=scheduled_end_time,
            tz=tz,
        )

        if facility_id:
            customer_id = get_customer_id_by_facility_id(session=session, facility_id=facility_id)
        else:
            customer_id = None

        order = Order(
            order_type_id=order_type_id,
            order_status_id=order_status_id,
            ext_id=ext_id.strip() if ext_id else ext_id,
            utility_id=utility_id,
            facility_id=facility_id,
            customer_id=customer_id,
            checklist_id=checklist_id,
            assigned_to_user_id=technician_id,
            description=description.strip() if description else description,
            scheduled_start_at=start_datetime,
            scheduled_end_at=end_datetime,
            created_by=user_id,
        )

        result = create_order(session=session, order=order)

        if result.ok:
            banner_container.success(
                translation.success_message.format(order_id=order.order_id), icon=ICON_SUCCESS
            )
        else:
            banner_container.error(translation.error_message, icon=ICON_ERROR)

        return order
