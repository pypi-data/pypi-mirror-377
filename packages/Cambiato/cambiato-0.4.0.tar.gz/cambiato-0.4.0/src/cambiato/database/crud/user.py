r"""Functions for working with user related models."""

# Third party
import pandas as pd
from sqlalchemy import select

# Local
from cambiato.database.core import Session
from cambiato.database.models import CustomRole, User
from cambiato.database.models.default import technician
from cambiato.models.dataframe import UserDataFrameModel


def get_all_technicians(_session: Session) -> UserDataFrameModel:
    r"""Get all active technicians from the database.

    Parameters
    ----------
    _session : Session
        An active database session.

    Returns
    -------
    cambiato.models.UserDataFrameModel
        The technicians retrieved from the database.
    """

    c_user_id = UserDataFrameModel.c_user_id
    c_displayname = UserDataFrameModel.c_displayname

    query = (
        select(User.user_id.label(c_user_id), User.displayname.label(c_displayname))
        .join(User.custom_roles.and_(CustomRole.role_id == technician.role_id))
        .where(User.disabled == False)  # noqa: E712
        .order_by(User.displayname)
    )

    df = pd.read_sql_query(  # type: ignore[call-overload]
        sql=query,
        con=_session.bind,
        dtype={col: UserDataFrameModel.dtypes[col] for col in (c_user_id, c_displayname)},
        dtype_backend='pyarrow',
    ).set_index(UserDataFrameModel.index_cols)

    return UserDataFrameModel(df=df)
