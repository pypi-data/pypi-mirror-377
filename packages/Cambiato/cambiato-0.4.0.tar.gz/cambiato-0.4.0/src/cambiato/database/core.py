r"""The core database functionality."""

# Standard library
import logging
from collections.abc import Sequence
from typing import Any, NamedTuple, TypeAlias

# Third party
from streamlit_passwordless.database import URL as URL
from streamlit_passwordless.database import Session as Session
from streamlit_passwordless.database import SessionFactory as SessionFactory
from streamlit_passwordless.database import create_session_factory as create_session_factory

# Local
from cambiato import exceptions
from cambiato.core import OperationResult

logger = logging.getLogger(__name__)

Row: TypeAlias = dict[str, Any]
PrimaryKey: TypeAlias = int | str


class ChangedDatabaseRows(NamedTuple):
    r"""Information about rows that have changed for a table.

    Parameters
    ----------
    edited_rows : Sequence[dict[str, Any]] or dict[str, Any] or None, default None
        Rows that have been edited and should be updated in the database.

    added_rows : Sequence[dict[str, Any]] or dict[str, Any] or None, default None
        Rows that have been added and should be added to the database.

    deleted_rows : Sequence[int | str] or None, default None
        Rows that have been deleted and should be deleted from the database.
        The sequence should contain the primary keys of the rows to delete.
    """

    edited_rows: Sequence[Row] | Row | None = None
    added_rows: Sequence[Row] | Row | None = None
    deleted_rows: Sequence[PrimaryKey] | None = None


def commit(session: Session, error_msg: str = 'Error committing transaction!') -> OperationResult:
    r"""Commit a database transaction.

    session : cambiato.db.Session
        An active database session.

    error_msg : str, default 'Error committing transaction!'
        An error message to add if an exception is raised when committing the transaction.

    Returns
    -------
    result : cambiato.OperationResult
        The result of committing the transaction.
    """

    try:
        session.commit()
    except exceptions.SQLAlchemyError as e:
        long_msg = f'{error_msg}\n{e!s}'
        logger.error(long_msg)
        result = OperationResult(ok=False, short_msg=error_msg, long_msg=long_msg)
        session.rollback()
    else:
        result = OperationResult()

    return result
