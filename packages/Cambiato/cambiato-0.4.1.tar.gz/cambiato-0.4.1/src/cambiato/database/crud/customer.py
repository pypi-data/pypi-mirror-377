r"""Functions for working with customer related models."""

# Third party
from sqlalchemy import select

# Local
from cambiato.database.core import Session
from cambiato.database.models import Customer, Facility


def get_customer_id_by_facility_id(session: Session, facility_id: int) -> int | None:
    r"""Get a customer ID by a facility that the customer owns.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    facility_id : int
        The unique ID of the facility to filter by.

    Returns
    -------
    int or None
        The customer_id of the customer who owns the facility or None
        if no customer was found for supplied `facility_id`.
    """

    query = (
        select(Customer.customer_id)
        .select_from(Facility)
        .join(Facility.customer)
        .where(Facility.facility_id == facility_id)
    )

    return session.scalars(query).one_or_none()
