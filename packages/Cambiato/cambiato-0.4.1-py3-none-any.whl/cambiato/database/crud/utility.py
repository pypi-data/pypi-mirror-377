r"""Functions for working with the Utility model."""

# Third party
import pandas as pd
from sqlalchemy import select

# Local
from cambiato.database.core import Session
from cambiato.database.models import Utility
from cambiato.models import UtilityDataFrameModel
from cambiato.translations import TranslationMapping, translate_dataframe


def get_all_utilities(
    _session: Session, translation: TranslationMapping | None = None
) -> UtilityDataFrameModel:
    r"""Get all utilities from the database.

    Parameters
    ----------
    _session : Session
        An active database session.

    translation : Mapping[int, str] or None, default None
        The translations for the names of the default utilities.

    Returns
    -------
    cambiato.models.UtilityDataFrameModel
        The utilities retrieved from the database.
    """

    c_utility_id = UtilityDataFrameModel.c_utility_id
    c_name = UtilityDataFrameModel.c_name

    query = select(Utility.utility_id.label(c_utility_id), Utility.name.label(c_name)).order_by(
        Utility.utility_id
    )

    df = pd.read_sql_query(  # type: ignore[call-overload]
        sql=query,
        con=_session.bind,
        dtype={col: UtilityDataFrameModel.dtypes[col] for col in (c_utility_id, c_name)},
        dtype_backend='pyarrow',
    ).set_index(UtilityDataFrameModel.index_cols)

    if translation:
        df = translate_dataframe(df=df, translation=translation, columns=[c_name])

    return UtilityDataFrameModel(df=df)
