r"""The entry point of the Cambiato web app."""

# Standard library
from pathlib import Path

# Third party
import streamlit as st
import streamlit_passwordless as stp

# Local
from cambiato.app._pages import Pages
from cambiato.app.auth import get_current_user, is_authenticated
from cambiato.app.components.sidebar import sidebar

APP_PATH = Path(__file__)


def main() -> None:
    r"""The page router of the Cambiato web app."""

    stp.init_session_state()
    user = get_current_user()
    _is_authenticated = is_authenticated(user=user)

    pages = [
        st.Page(page=Pages.HOME, title='Home'),
        st.Page(page=Pages.SIGN_IN, title='Sign in and register', default=True),
        st.Page(page=Pages.ORDER, title='Order'),
    ]
    page = st.navigation(pages, position='top' if _is_authenticated else 'hidden')

    sidebar(is_authenticated=_is_authenticated, user=user)

    page.run()


if __name__ == '__main__':
    main()
