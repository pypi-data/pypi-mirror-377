r"""The core functionality of the package."""

# Standard library
from typing import NamedTuple

# Third party
from streamlit_passwordless import get_current_user as get_current_user


class OperationResult(NamedTuple):
    r"""The result of a function or method call.

    Should be returned from a function or method call to provide
    context weather the operation was successful or not.

    Parameters
    ----------
    ok : bool, default True
        True if the operation was successful and False otherwise.

    short_msg : str, default ''
        A short optional message that describes the reason for the result.
        Safe to display to the user.

    long_msg : str, default ''
        An longer message that further describes the result. May contain
        sensitive information and should not be displayed to the user.
    """

    ok: bool = True
    short_msg: str = ''
    long_msg: str = ''
