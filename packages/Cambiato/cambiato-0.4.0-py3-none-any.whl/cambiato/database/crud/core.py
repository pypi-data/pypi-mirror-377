r"""Core functions to build SQL statements."""

# Third party
from sqlalchemy import String, case, cast, func, literal
from sqlalchemy.sql import ColumnElement

# Local
from cambiato.database.models import Location


def build_full_address_column(apartment_nr_prefix: str = '') -> ColumnElement[str]:
    r"""Construct a full address column.

    The address information comes from the address component
    columns of class:`cambiato.db.models.Location` model.

    Parameters
    ----------
    apartment_nr_prefix : str, default ''
        The prefix to use for the apartment number. E.g. "lgh" in Swedish.
        The default omits the prefix.

    Returns
    -------
    sqlalchemy.sql.ColumnElement[str]
        The full address string column.
    """

    space = literal(' ')

    apartment_col = case(
        (
            Location.apartment_number.isnot(None),
            literal(apartment_nr_prefix)
            .concat(space)
            .concat(cast(Location.apartment_number, String)),
        ),
        else_=literal(''),
    )

    return (
        func.coalesce(Location.street_name, '')
        .concat(space)
        .concat(func.coalesce(cast(Location.street_number, String), ''))
        .concat(func.coalesce(Location.street_number_suffix, ''))
        .concat(space)
        .concat(apartment_col)
        .concat(space)
        .concat(func.coalesce(cast(Location.zip_code, String), ''))
        .concat(space)
        .concat(func.coalesce(Location.city, ''))
    )
