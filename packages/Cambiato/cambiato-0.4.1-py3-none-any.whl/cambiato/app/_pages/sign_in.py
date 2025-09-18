r"""The entry point of the sign in page."""

# Standard library
from pathlib import Path

# Third party
import streamlit as st

# Local
from cambiato.app.auth import is_authenticated
from cambiato.app.config import (
    APP_HOME_PAGE_URL,
    APP_ISSUES_PAGE_URL,
    MAINTAINER_INFO,
)
from cambiato.app.controllers.sign_in import controller
from cambiato.app.setup import bwp_client, session_factory

SIGN_IN_PATH = Path(__file__)

ABOUT = f"""Sign in to Cambiato or register an account.

{MAINTAINER_INFO}
"""


def sign_in_page() -> None:
    r"""Run the sign in page of Cambiato."""

    _is_authenticated = is_authenticated()
    st.set_page_config(
        page_title='Cambiato - Sign in',
        page_icon=':sparkles:',
        layout='centered',
        menu_items={
            'Get Help': APP_HOME_PAGE_URL,
            'Report a bug': APP_ISSUES_PAGE_URL,
            'About': ABOUT,
        },
        initial_sidebar_state='auto' if _is_authenticated else 'collapsed',
    )

    with session_factory() as session:
        controller(session=session, client=bwp_client, is_authenticated=_is_authenticated)


if __name__ in {'__main__', '__page__'}:
    sign_in_page()
