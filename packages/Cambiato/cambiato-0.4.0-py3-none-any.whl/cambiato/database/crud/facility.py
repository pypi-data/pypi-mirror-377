r"""Functions for working with facility related models."""

# Standard library
from collections.abc import Sequence

# Third party
import pandas as pd
from sqlalchemy import select

# Local
from cambiato.database.core import Session
from cambiato.database.crud.core import build_full_address_column
from cambiato.database.models import Facility
from cambiato.models import FacilityDataFrameModel


def get_all_facilities(
    _session: Session, utility_ids: Sequence[int] | None = None
) -> FacilityDataFrameModel:
    r"""Get all facilities from the database.

    Parameters
    ----------
    session : Session
        An active database session.

    utility_ids : Sequence[int] or None, default None
        The ID:s of the utilities to filter by. If None filtering by utility is omitted.

    Returns
    -------
    cambiato.models.FacilityDataFrameModel
        The facilities retrieved from the database.
    """

    c_facility_id = FacilityDataFrameModel.c_facility_id
    c_ean = FacilityDataFrameModel.c_ean
    c_address = FacilityDataFrameModel.c_address

    query = (
        select(
            Facility.facility_id.label(c_facility_id),
            Facility.ean.label(c_ean),
            build_full_address_column().label(c_address),
        )
        .join(Facility.location)
        .order_by(Facility.ean)
    )

    if utility_ids:
        query = query.where(Facility.utility_id.in_(utility_ids))

    df = pd.read_sql_query(  # type: ignore[call-overload]
        sql=query,
        con=_session.bind,
        dtype={
            col: FacilityDataFrameModel.dtypes[col] for col in (c_facility_id, c_ean, c_address)
        },
        dtype_backend='pyarrow',
    ).set_index(FacilityDataFrameModel.index_cols)

    return FacilityDataFrameModel(df=df)
