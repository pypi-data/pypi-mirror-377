r"""Functions for working with order related models."""

# Standard library
from collections.abc import Sequence
from zoneinfo import ZoneInfo

# Third party
import pandas as pd
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.orm import aliased

# Local
from cambiato.core import OperationResult
from cambiato.database.core import ChangedDatabaseRows, Session, commit
from cambiato.database.crud.core import build_full_address_column
from cambiato.database.models import Facility, Order, OrderStatus, OrderType, User
from cambiato.models.dataframe import (
    OrderDataFrameModel,
    OrderStatusDataFrameModel,
    OrderTypeDataFrameModel,
)
from cambiato.translations import TranslationMapping, translate_dataframe


def get_all_order_types(
    _session: Session,
    utility_ids: Sequence[int] | None = None,
    translation: TranslationMapping | None = None,
) -> OrderTypeDataFrameModel:
    r"""Get all order types from the database.

    Parameters
    ----------
    _session : cambiato.db.Session
        An active database session.

    utility_ids : Sequence[int] or None, default None
        The ID:s of the utilities to filter by in addition to the non-utility specific
        order types. If None all order types without a specified utility are included.

    translation : Mapping[int, str] or None, default None
        The translations for the names of the default order types.

    Returns
    -------
    cambiato.models.OrderTypeDataFrameModel
        The order types retrieved from the database.
    """

    c_order_type_id = OrderTypeDataFrameModel.c_order_type_id
    c_name = OrderTypeDataFrameModel.c_name

    query = select(
        OrderType.order_type_id.label(c_order_type_id), OrderType.name.label(c_name)
    ).order_by(OrderType.order_type_id)

    if utility_ids:
        query = query.where(
            or_(OrderType.utility_id.in_(utility_ids), OrderType.utility_id.is_(None))
        )
    else:
        query = query.where(OrderType.utility_id.is_(None))

    df = pd.read_sql_query(
        sql=query,
        con=_session.bind,  # type: ignore[arg-type]
        dtype={col: OrderTypeDataFrameModel.dtypes[col] for col in (c_order_type_id, c_name)},
    ).set_index(OrderTypeDataFrameModel.index_cols)

    if translation:
        df = translate_dataframe(df=df, translation=translation, columns=[c_name])

    return OrderTypeDataFrameModel(df=df)


def get_all_order_statuses(
    _session: Session,
    utility_ids: Sequence[int] | None = None,
    translation: TranslationMapping | None = None,
) -> OrderStatusDataFrameModel:
    r"""Get all order statuses from the database.

    Parameters
    ----------
    _session : cambiato.db.Session
        An active database session.

    utility_ids : Sequence[int] or None, default None
        The ID:s of the utilities to filter by in addition to the non-utility specific
        order statuses. If None all order statues without a specified utility are included.

    translation : Mapping[int, str] or None, default None
        The translations for the names of the default order statuses.

    Returns
    -------
    cambiato.models.OrderStatusThinDataFrameModel
        The order statuses retrieved from the database.
    """

    c_order_status_id = OrderStatusDataFrameModel.c_order_status_id
    c_name = OrderStatusDataFrameModel.c_name

    query = select(
        OrderStatus.order_status_id.label(c_order_status_id), OrderStatus.name.label(c_name)
    ).order_by(OrderStatus.order_status_id)

    if utility_ids:
        query = query.where(
            or_(OrderStatus.utility_id.in_(utility_ids), OrderStatus.utility_id.is_(None))
        )
    else:
        query = query.where(OrderStatus.utility_id.is_(None))

    df = pd.read_sql_query(  # type: ignore[call-overload]
        sql=query,
        con=_session.bind,
        dtype={col: OrderStatusDataFrameModel.dtypes[col] for col in (c_order_status_id, c_name)},
        dtype_backend='pyarrow',
    ).set_index(OrderStatusDataFrameModel.index_cols)

    if translation:
        df = translate_dataframe(df=df, translation=translation, columns=[c_name])

    return OrderStatusDataFrameModel(df=df)


def get_all_active_orders(
    _session: Session,
    utility_ids: Sequence[int] | None = None,
    order_types: Sequence[int] | None = None,
    order_statuses: Sequence[int] | None = None,
    tz: ZoneInfo | None = None,
    order_type_trans: TranslationMapping | None = None,
    order_status_trans: TranslationMapping | None = None,
) -> OrderDataFrameModel:
    r"""Get all active orders from the database.

    An active order is defined as an order with a status that is not of state "completed".

    Parameters
    ----------
    _session : cambiato.db.Session
        An active database session.

    utility_ids : Sequence[int] or None, default None
        The ID:s of the utilities to filter by. If None filtering by
        column utility_id is omitted.

    order_types : Sequence[int] or None, default None
        The ID:s of the order types to filter by. If None filtering by
        column order_type_id is omitted.

    order_statuses : Sequence[int] or None, default None
        The ID:s of the order statuses to filter by. If None filtering by
        column order_status_id is omitted.

    tz : zoneinfo.ZoneInfo or None, default None
        The timezone to convert the datetime columns into. If None conversion from
        the database UTC timezone is omitted.

    order_type_trans : cambiato.translations.TranslationMapping or None, default None
        Translations for the names of the order types. If None no translation is performed.

    order_status_trans: cambiato.translations.TranslationMapping or None, default None
        Translations for the names of the order statuses. If None no translation is performed.

    Returns
    -------
    cambiato.models.OrderDataFrameModel
        The orders retrieved from the database.
    """

    c_order_id = OrderDataFrameModel.c_order_id
    c_order_type_id = OrderDataFrameModel.c_order_type_id
    c_order_type_name = OrderDataFrameModel.c_order_type_name
    c_order_status_id = OrderDataFrameModel.c_order_status_id
    c_order_status_name = OrderDataFrameModel.c_order_status_name
    c_facility_ean = OrderDataFrameModel.c_facility_ean
    c_address = OrderDataFrameModel.c_address
    c_ext_id = OrderDataFrameModel.c_ext_id
    c_description = OrderDataFrameModel.c_description
    c_assigned_to_displayname = OrderDataFrameModel.c_assigned_to_displayname
    c_scheduled_start_at = OrderDataFrameModel.c_scheduled_start_at
    c_scheduled_end_at = OrderDataFrameModel.c_scheduled_end_at
    c_created_by = OrderDataFrameModel.c_created_by
    c_created_at = OrderDataFrameModel.c_created_at
    c_updated_by = OrderDataFrameModel.c_updated_by
    c_updated_at = OrderDataFrameModel.c_updated_at

    created_by_alias = aliased(User, name='created_by_user')
    updated_by_alias = aliased(User, name='updated_by_user')

    query = (
        select(
            Order.order_id.label(c_order_id),
            OrderType.order_type_id.label(c_order_type_id),
            OrderType.name.label(c_order_type_name),
            OrderStatus.order_status_id.label(c_order_status_id),
            OrderStatus.name.label(c_order_status_name),
            Facility.ean.label(c_facility_ean),
            build_full_address_column().label(c_address),
            Order.ext_id.label(c_ext_id),
            Order.description.label(c_description),
            User.displayname.label(c_assigned_to_displayname),
            Order.scheduled_start_at.label(c_scheduled_start_at),
            Order.scheduled_end_at.label(c_scheduled_end_at),
            created_by_alias.displayname.label(c_created_by),
            Order.created_at.label(c_created_at),
            updated_by_alias.displayname.label(c_updated_by),
            Order.updated_at.label(c_updated_at),
        )
        .select_from(Order)
        .join(Order.order_type)
        .join(Order.order_status)
        .join(Order.assigned_to, isouter=True)
        .join(Order.facility, isouter=True)
        .join(Facility.location, isouter=True)
        .join(created_by_alias, created_by_alias.user_id == Order.created_by)
        .join(updated_by_alias, updated_by_alias.user_id == Order.updated_by, isouter=True)
        .where(OrderStatus.is_completed == False)  # noqa: E712
        .order_by(OrderStatus.order_status_id, Order.created_at.desc())
    )

    if utility_ids:
        query = query.where(Order.utility_id.in_(utility_ids))

    if order_types:
        query = query.where(Order.order_type_id.in_(order_types))

    if order_statuses:
        query = query.where(Order.order_status_id.in_(order_statuses))

    df = pd.read_sql_query(
        sql=query,
        con=_session.get_bind(),
        dtype_backend='pyarrow',
    ).set_index(OrderDataFrameModel.index_cols)

    if order_type_trans and order_status_trans:
        df = translate_dataframe(
            df=df,
            translation=(order_type_trans, order_status_trans),
            columns=(c_order_type_name, c_order_status_name),
            id_column=(c_order_type_id, c_order_status_id),
        )

    orders = OrderDataFrameModel(df=df.drop(columns=[c_order_type_id, c_order_status_id]))
    orders.localize_and_convert_timezone(
        target_tz=tz if tz is None else str(tz),
        ensure_datetime_cols=(c_scheduled_start_at, c_scheduled_end_at, c_created_at, c_updated_at),
        copy=False,
    )

    return orders


def create_order(session: Session, order: Order) -> OperationResult:
    r"""Create a new order in the database.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    order : cambiato.db.models.Order
        The order to save to the database.

    Returns
    -------
    cambiato.OperationResult
        The result of saving the order to the database.
    """

    session.add(order)
    return commit(session=session, error_msg='Unexpected error when saving order to database!')


def process_changed_orders(
    session: Session, changed_orders: ChangedDatabaseRows
) -> OperationResult:
    r"""Process the changes (update, insert or delete) for selected orders.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    changed_orders : cambiato.db.ChangedDatabaseRows
        The changed orders to process.

    Returns
    -------
    cambiato.OperationResult
        The result of processing the changed orders in the database.
    """

    if updated := changed_orders.edited_rows:
        session.execute(update(Order), updated)
    if added := changed_orders.added_rows:
        session.execute(insert(Order), added)
    if deleted := changed_orders.deleted_rows:
        session.execute(delete(Order).where(Order.order_id.in_(deleted)))

    return commit(session=session, error_msg='Error performing order updates!')
