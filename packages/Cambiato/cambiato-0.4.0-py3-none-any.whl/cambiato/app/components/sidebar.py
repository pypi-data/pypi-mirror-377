r"""Sidebar components."""

# Third party
import streamlit as st

# Local
from cambiato.app.components.buttons import sign_out_button
from cambiato.models import User


def sidebar(is_authenticated: bool, user: User | None = None) -> None:
    r"""Render the sidebar.

    Parameters
    ----------
    is_authenticated : bool
        True if the `user` is authenticated and False otherwise.

    user : cambiato.models.User or None, default None
        The user accessing the application. If None the user is not signed in yet.
    """

    if not is_authenticated:
        return

    with st.sidebar:
        sign_out_button(user=user)
