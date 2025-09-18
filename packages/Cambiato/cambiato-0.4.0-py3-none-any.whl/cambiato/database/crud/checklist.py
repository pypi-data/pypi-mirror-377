r"""Functions for working with checklist related models."""

# Standard library
from collections.abc import Sequence

# Third party
import pandas as pd
from sqlalchemy import or_, select

# Local
from cambiato.database.core import Session
from cambiato.database.models import Checklist
from cambiato.models.dataframe import ChecklistDataFrameModel


def get_all_checklists(
    _session: Session, utility_ids: Sequence[int] | None = None
) -> ChecklistDataFrameModel:
    r"""Get all checklists from the database.

    Parameters
    ----------
    _session : Session
        An active database session.

    utility_ids : Sequence[int] or None, default None
        The ID:s of the utilities to filter by. If None filtering by utility is omitted.

    Returns
    -------
    cambiato.models.ChecklistDataFrameModel
        The order types retrieved from the database.
    """

    c_checklist_id = ChecklistDataFrameModel.c_checklist_id
    c_name = ChecklistDataFrameModel.c_name

    query = select(
        Checklist.checklist_id.label(c_checklist_id), Checklist.name.label(c_name)
    ).order_by(Checklist.checklist_id)

    if utility_ids:
        query = query.where(
            or_(Checklist.utility_id.in_(utility_ids), Checklist.utility_id.is_(None))
        )

    df = pd.read_sql_query(
        sql=query,
        con=_session.bind,  # type: ignore[arg-type]
        dtype={col: ChecklistDataFrameModel.dtypes[col] for col in (c_checklist_id, c_name)},
    ).set_index(ChecklistDataFrameModel.index_cols)

    return ChecklistDataFrameModel(df=df)
