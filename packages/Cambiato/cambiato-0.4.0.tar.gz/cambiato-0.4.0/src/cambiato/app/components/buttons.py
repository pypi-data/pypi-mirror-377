r"""Button components."""

# Standard library
from typing import Literal, TypeAlias
from zoneinfo import ZoneInfo

# Third party
import streamlit as st

# Local
from cambiato.app.auth import get_current_user, sign_out
from cambiato.app.components import keys
from cambiato.app.components.forms.create_order_form import create_order_form
from cambiato.database import Session
from cambiato.models import User
from cambiato.models.dataframe import (
    ChecklistDataFrameModel,
    FacilityDataFrameModel,
    OrderStatusDataFrameModel,
    OrderTypeDataFrameModel,
    UserDataFrameModel,
)
from cambiato.translations import CreateOrderForm

ButtonType: TypeAlias = Literal['primary', 'secondary', 'tertiary']


def sign_out_button(
    user: User | None = None,
    label: str = 'Sign out',
    icon: str | None = None,
    button_type: ButtonType = 'primary',
    help_text: str | None = None,
    use_container_width: bool = False,
) -> bool:
    r"""The sign out button to sign out a user from the application.

    If clicked the user is signed out from the application.
    The button is disabled if a user is not signed in.

    Parameters
    ----------
    user : cambiato.models.User or None, default None
        The user to sign out. If None the user is loaded from the session state.

    label : str, default 'Sign out'
        The label of the sign out button. GitHub-flavored Markdown is supported.

    icon : str or None, default None
        An optional icon to display next to the `label` of the button.
        See the `icon` parameter of :func:`streamlit.button` for more info.

    button_type : Literal['primary', 'secondary', 'tertiary'], default 'primary'
        The styling of the button. Emulates the `type` parameter of :func:`streamlit.button`.

    help_text : str or None, default None
        An optional help text to display when hovering over the button.

    use_container_width : bool, default False
        If True the button will take upp the full width of the parent container
        and if False it will be sized to fit the content of `label` and `icon`.

    Returns
    -------
    clicked : bool
        True if the button was clicked and False otherwise.
    """

    user = get_current_user() if user is None else user

    return st.button(
        label=label,
        icon=icon,
        type=button_type,
        help=help_text,
        use_container_width=use_container_width,
        disabled=user is None or not user.is_authenticated,
        on_click=sign_out,
        kwargs={'user': user},
    )


def create_order_button(
    label: str,
    session: Session,
    utility_id: int | None,
    order_types: OrderTypeDataFrameModel,
    order_statuses: OrderStatusDataFrameModel,
    facilities: FacilityDataFrameModel,
    checklists: ChecklistDataFrameModel,
    technicians: UserDataFrameModel,
    translation: CreateOrderForm,
    tz: ZoneInfo,
    user_id: str | None = None,
    disabled: bool = False,
    icon: str | None = None,
    button_type: ButtonType = 'secondary',
    help_text: str | None = None,
    key: str = keys.CREATE_ORDER_BUTTON,
) -> bool:
    r"""A button that opens the `create_order_form` in a dialog frame.

    Parameters
    ----------
    label : str
        The label of the button.

    session : cambiato.db.Session
        An active database session.

    utility_id : int or None
        The primary key of the utility that the created order should belong to.
        If None the button will be disabled.

    order_types : cambiato.models.OrderTypeDataFrameModel
        The selectable order types of the order to create.

    order_statuses : cambiato.models.OrderStatusDataFrameModel
        The selectable order statuses of the order to create.

    facilities : cambiato.models.FacilityDataFrameModel
        The selectable facilities that can be assigned to the order.

    checklists : cambiato.models.ChecklistDataFrameModel
        The selectable checklists that can be assigned to the order.

    technicians : cambiato.models.UserDataFrameModel
        The selectable technicians that can be assigned to the order.

    translation : cambiato.translations.CreateOrderForm
        The language translations of the form.

    tz : zoneinfo.ZoneInfo
        The timezone of the entered datetime values of the form.

    user_id : str or None, default None
        The ID of the user that is creating the order.

    disabled : bool, default False
        True if the button should be disabled and False otherwise.

    icon: str or None, default None
        An optional icon to display next to the `label` on the button.

    button_type : Literal['primary', 'secondary', 'tertiary'], default 'secondary'
        The styling of the button.

    help_text: str or None, default None
        An optional help text to display when hovering over the button.

    key : str, default cambiato.app.components.keys.CREATE_ORDER_BUTTON
        The unique identifier of the button in the session state.

    Returns
    -------
    bool
        True if the button was clicked and False otherwise.
    """

    create_order_on_click = st.dialog(title=translation.title)(create_order_form)  # type: ignore[type-var]

    return st.button(
        label=label,
        disabled=disabled or utility_id is None,
        icon=icon,
        type=button_type,
        help=help_text,
        on_click=create_order_on_click,  # type: ignore[arg-type]
        kwargs={
            'session': session,
            'utility_id': utility_id,
            'order_types': order_types,
            'order_statuses': order_statuses,
            'facilities': facilities,
            'checklists': checklists,
            'technicians': technicians,
            'translation': translation,
            'tz': tz,
            'user_id': user_id,
            'border': False,
            'title': False,
        },
        key=key,
    )
